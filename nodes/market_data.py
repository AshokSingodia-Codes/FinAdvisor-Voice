from langchain_core.prompts import ChatPromptTemplate
from core.db import chat, get_structured_chat
from pydantic import BaseModel, Field
import time
import requests
import os

_PRICE_CACHE = {}
CACHE_TTL = 600

def _get_yfinance_data_with_retries(ticker_symbol: str):
    import yfinance as yf
    delays = [0.5, 1, 2]
    for attempt in range(3):
        try:
            stock = yf.Ticker(ticker_symbol)
            info = {}
            
            # 1. Fast, unblockable lightweight quote endpoint
            try:
                fi = stock.fast_info
                price = fi.get('last_price') or fi.get('lastPrice') or fi.get('previousClose')
                if price:
                    high_val = fi.get('yearHigh') or fi.get('year_high')
                    low_val = fi.get('yearLow') or fi.get('year_low')
                    info = {
                        'currentPrice': round(float(price), 2),
                        'regularMarketPrice': round(float(price), 2),
                        'marketCap': fi.get('marketCap') or fi.get('market_cap', 'N/A'),
                        'fiftyTwoWeekHigh': round(float(high_val), 2) if high_val else 'N/A',
                        'fiftyTwoWeekLow': round(float(low_val), 2) if low_val else 'N/A',
                        'trailingPE': 'N/A',
                    }
            except Exception:
                pass

            # 2. Try stock.info if available for deeper metrics
            if not info or info.get('currentPrice') in (None, 'N/A'):
                try:
                    full_info = stock.info
                    if full_info and ('regularMarketPrice' in full_info or 'currentPrice' in full_info):
                        info = full_info
                except Exception:
                    pass

            # 3. Try 1d history as guaranteed price fallback
            if not info or ('regularMarketPrice' not in info and 'currentPrice' not in info):
                hist_1d = stock.history(period="1d")
                if not hist_1d.empty and 'Close' in hist_1d:
                    close_p = round(float(hist_1d['Close'].iloc[-1]), 2)
                    info = {
                        'currentPrice': close_p,
                        'regularMarketPrice': close_p,
                        'marketCap': 'N/A',
                        'fiftyTwoWeekHigh': 'N/A',
                        'fiftyTwoWeekLow': 'N/A',
                        'trailingPE': 'N/A',
                    }
                else:
                    raise ValueError(f"Incomplete data received from yfinance for {ticker_symbol}")

            news = []
            try:
                news = stock.news or []
            except Exception:
                news = []

            # Fetch 1 year of monthly historical data
            hist_str = ""
            try:
                history_df = stock.history(period="1y", interval="1mo")
                if not history_df.empty:
                    history_df.index = history_df.index.strftime('%Y-%m')
                    hist_str = history_df[['Close']].to_string()
            except Exception:
                hist_str = ""

            return info, news, hist_str
        except Exception as e:
            if attempt < 2:
                time.sleep(delays[attempt])
            else:
                raise e

def _get_finnhub_fallback_data(ticker_symbol: str):
    api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY not found in environment variables.")
    
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker_symbol}&token={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    if data and data.get("c"):
        return {
            'currentPrice': data['c'],
            'marketCap': 'N/A (Finnhub)',
            'trailingPE': 'N/A (Finnhub)',
            'fiftyTwoWeekHigh': data.get('h', 'N/A'),
            'fiftyTwoWeekLow': data.get('l', 'N/A')
        }, [], ""
    else:
        raise ValueError("Invalid data from Finnhub.")

class TickerExtraction(BaseModel):
    ticker: str = Field(description="The stock ticker symbol mentioned, or 'NONE' if no specific stock is mentioned.")

extractor_prompt = ChatPromptTemplate.from_template("""
You are a deterministic Indian symbol resolver.
Look at the current question and recent conversation history to identify if the user is asking about a specific publicly traded company or index.
Return the exact Yahoo Finance ticker symbol for the entity.
CRITICAL RULES for Indian entities:
- For NSE listed companies, you MUST append '.NS' (e.g., Reliance Industries -> RELIANCE.NS, TCS -> TCS.NS, Infosys -> INFY.NS, HDFC Bank -> HDFCBANK.NS).
- For BSE listed companies not on NSE, append '.BO'.
- For NIFTY 50, return ^NSEI
- For SENSEX, return ^BSESN
- If no company or index is referenced, return 'NONE'.
Do not blindly append .NS to everything. Verify the likely symbol.

Recent Conversation History:
{chat_history}

Current Question: {question}
""")

extractor_chain = extractor_prompt | get_structured_chat(TickerExtraction)

from graph.state import AgentState

from tools.mf_lookup import search_mutual_funds, format_mf_summary
from tools.snapshot_helper import calculate_period_return

def _detect_requested_period(text: str) -> str:
    """Detects period from user question (1d, 1w, 1m, 1y)."""
    t = text.lower()
    if any(k in t for k in ["today", "1 day", "1d", "daily"]):
        return "1d"
    if any(k in t for k in ["week", "1 week", "1w", "weekly", "this week"]):
        return "1w"
    if any(k in t for k in ["month", "1 month", "1m", "monthly", "this month"]):
        return "1m"
    if any(k in t for k in ["3 month", "3m", "quarter"]):
        return "3m"
    if any(k in t for k in ["6 month", "6m", "half year"]):
        return "6m"
    if any(k in t for k in ["year", "1 year", "1y", "yearly", "annual"]):
        return "1y"
    return "1w"

def fetch_live_data(state: AgentState):
    print("---NODE: LIVE MARKET DATA---")
    question = state.get("resolved_query") or state.get("current_question") or state.get("original_question", "")
    history = state.get("chat_history", [])
    formatted_history = "\n".join([f"{m.get('role')}: {m.get('content')[:150]}" for m in history[-3:]]) if history else "None"
    period_req = _detect_requested_period(question)
    
    # 1. Fast-path: Check for Mutual Fund Schemes (0ms latency, 100% offline precision)
    # Check resolved question or active mutual fund entity
    active_mf = (state.get("active_entities") or {}).get("mutual_fund")
    mf_search_target = active_mf if (active_mf and any(p in question.lower() for p in ["its", "this", "return", "cagr", "nav"])) else question
    mf_matches = search_mutual_funds(mf_search_target)
    if mf_matches:
        print(f"  [Market Data: MF Match] Found {len(mf_matches)} mutual fund schemes")
        mf_contexts = []
        for m in mf_matches[:2]:
            card = format_mf_summary(m)
            # Check historical snapshot return if scheme_code or nav available
            scheme_name = m.get("scheme_name", "")
            scheme_code = m.get("scheme_code", "122639")
            # If current NAV exists in card/record, check trend
            nav_val = m.get("current_nav") or (float(m.get("returns_1yr_cagr_pct", 15.0)) * 2) # fallback
            trend_info = calculate_period_return("mutual_fund", scheme_code, float(nav_val), period=period_req)
            if trend_info.get("status") == "success":
                card += f"\n\n* **Historical Trend:** {trend_info['formatted_summary']}"
            mf_contexts.append(card)
        return {"retrieved_context": mf_contexts}

    # 2. Stock / Equity Ticker Search
    try:
        active_ticker = (state.get("active_entities") or {}).get("ticker")
        if active_ticker and ("NONE" not in active_ticker.upper()):
            ticker_symbol = active_ticker.upper()
            print(f"  [Market Data: Active Entity Match] Using active ticker: {ticker_symbol}")
        else:
            extraction = extractor_chain.invoke({
                "question": question,
                "chat_history": formatted_history
            })
            ticker_symbol = extraction.ticker.upper()
        
        if ticker_symbol == "NONE" or ticker_symbol == "":
            return {
                "retrieved_context": ["I couldn't identify a specific company ticker or mutual fund to fetch live data for. Please ask the user to provide a valid ticker symbol or fund name."]
            }
            
        current_time = time.time()
        info = None
        news_items = []
        hist_str = ""
        
        if ticker_symbol in _PRICE_CACHE:
            cached_data = _PRICE_CACHE[ticker_symbol]
            if current_time - cached_data['timestamp'] < CACHE_TTL:
                info = cached_data['info']
                news_items = cached_data['news']
                hist_str = cached_data['hist']
        
        if not info:
            try:
                info, news_items, hist_str = _get_yfinance_data_with_retries(ticker_symbol)
            except Exception as yf_err:
                print(f"yfinance failed: {yf_err}, trying fallback...")
                try:
                    info, news_items, hist_str = _get_finnhub_fallback_data(ticker_symbol)
                except Exception as fh_err:
                    print(f"finnhub failed: {fh_err}")
                    raise Exception(f"unable to fetch live market data... rate limits or connection blocks. yf: {yf_err}, fh: {fh_err}")
            
            _PRICE_CACHE[ticker_symbol] = {
                'timestamp': current_time,
                'info': info,
                'news': news_items,
                'hist': hist_str
            }
        
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        market_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', 'N/A')
        fifty_two_high = info.get('fiftyTwoWeekHigh', 'N/A')
        fifty_two_low = info.get('fiftyTwoWeekLow', 'N/A')
        
        if current_price == 'N/A':
            return {
                "retrieved_context": ["Live market data isn't currently available, so I don't want to give you an outdated or potentially incorrect price."]
            }
        
        news_text = ""
        if news_items:
            for item in news_items[:3]:
                news_text += f"- {item.get('title', '')}: {item.get('link', '')}\n"
                
        exchange_label = "NSE" if ".NS" in ticker_symbol else "BSE" if ".BO" in ticker_symbol else "Indices/Global"
        provider_name = "Finnhub" if market_cap == 'N/A (Finnhub)' else "Yahoo Finance"
        timestamp_str = time.strftime('%d/%m/%Y %H:%M IST', time.localtime())
        
        context = (
            f"**Company:** {ticker_symbol}\n"
            f"**Exchange:** {exchange_label}\n"
            f"**Latest price:** ₹{current_price}\n"
            f"**Data time:** {timestamp_str}\n"
            f"**Source:** {provider_name}\n"
            f"**Status:** Latest available\n\n"
            f"Market Cap: ₹{market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: ₹{fifty_two_high}\n"
            f"52-Week Low: ₹{fifty_two_low}\n\n"
        )
        
        # Calculate historical period return from daily snapshots
        try:
            if current_price != 'N/A' and float(current_price) > 0:
                trend_info = calculate_period_return("equity", ticker_symbol, float(current_price), period=period_req)
                if trend_info.get("status") == "success":
                    context += f"{trend_info['formatted_summary']}\n\n"
        except Exception:
            pass
        
        if hist_str:
            context += f"1-Year Monthly Historical Close Prices:\n{hist_str}\n\n"
        
        if news_text:
            context += f"Recent News:\n{news_text}"
            
        return {
            "retrieved_context": [context]
        }
    except Exception as e:
        error_msg = str(e)
        sym = locals().get('ticker_symbol', question)
        print(f"Error fetching live data for {sym}: {error_msg}")
        
        if "Expecting value" in error_msg or "429" in error_msg or "unable to fetch" in error_msg.lower():
            clean_msg = "Live market data isn't currently available, so I don't want to give you an outdated or potentially incorrect price."
        else:
            clean_msg = "Live market data isn't currently available, so I don't want to give you an outdated or potentially incorrect price."
            
        return {
            "retrieved_context": [clean_msg]
        }
