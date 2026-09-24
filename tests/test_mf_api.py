import requests
import json
import time

def test_mf_api():
    query = "Parag Parikh Flexi Cap"
    print(f"Searching for Mutual Fund: '{query}'...")
    t0 = time.time()
    
    # 1. Search scheme code
    search_url = f"https://api.mfapi.in/mf/search?q={requests.utils.quote(query)}"
    res = requests.get(search_url, timeout=5)
    t_search = time.time() - t0
    
    if res.status_code == 200:
        results = res.json()
        print(f"Found {len(results)} schemes in {t_search*1000:.1f}ms")
        if results:
            first = results[0]
            scheme_code = first.get("schemeCode")
            scheme_name = first.get("schemeName")
            print(f"Top Match: Code {scheme_code} - {scheme_name}")
            
            # 2. Fetch latest NAV
            t1 = time.time()
            detail_url = f"https://api.mfapi.in/mf/{scheme_code}/latest"
            d_res = requests.get(detail_url, timeout=5)
            t_detail = time.time() - t1
            
            if d_res.status_code == 200:
                data = d_res.json()
                meta = data.get("meta", {})
                nav_data = data.get("data", [])
                latest_nav = nav_data[0].get("nav") if nav_data else "N/A"
                nav_date = nav_data[0].get("date") if nav_data else "N/A"
                
                print(f"Latest NAV fetched in {t_detail*1000:.1f}ms:")
                print(f" • Scheme: {meta.get('scheme_name')}")
                print(f" • Fund House: {meta.get('fund_house')}")
                print(f" • Scheme Category: {meta.get('scheme_category')}")
                print(f" • NAV: ₹{latest_nav} (Date: {nav_date})")
    else:
        print(f"Search failed with HTTP {res.status_code}")

if __name__ == "__main__":
    test_mf_api()
