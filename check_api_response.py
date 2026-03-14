import httpx
import json

def check_api():
    url = "http://localhost:8000/api/immediate/picks/high-ev"
    try:
        resp = httpx.get(url)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Count: {len(data)}")
        if data:
            print("Picks Summary:")
            for item in data[:5]:
                print(f"- {item.get('player_name')} ({item.get('stat_type')}): {item.get('line')} @ {item.get('odds')} (EV: {item.get('ev_percentage')}%)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
