import pytest
from nodes.market_data import fetch_live_data, TickerExtraction

def test_fetch_live_data_with_ticker(mocker):
    # Mock LLM extractor
    mock_extractor = mocker.patch('nodes.market_data.extractor_chain')
    mock_extractor.invoke.return_value = TickerExtraction(ticker="AAPL")
    
    # Mock yfinance
    mock_yf = mocker.patch('nodes.market_data.yf.Ticker')
    mock_ticker = mock_yf.return_value
    mock_ticker.info = {
        'currentPrice': 150.0,
        'marketCap': '2T',
        'trailingPE': 25,
        'fiftyTwoWeekHigh': 200.0,
        'fiftyTwoWeekLow': 100.0
    }
    mock_ticker.news = []
    
    state = {"current_question": "How is Apple doing?"}
    result = fetch_live_data(state)
    
    assert "retrieved_context" in result
    assert "AAPL" in result["retrieved_context"][0]
    assert "150.0" in result["retrieved_context"][0]

def test_fetch_live_data_no_ticker(mocker):
    mock_extractor = mocker.patch('nodes.market_data.extractor_chain')
    mock_extractor.invoke.return_value = TickerExtraction(ticker="NONE")
    
    state = {"current_question": "What is inflation?"}
    result = fetch_live_data(state)
    
    assert "retrieved_context" in result
    assert "couldn't identify a specific company ticker" in result["retrieved_context"][0]
