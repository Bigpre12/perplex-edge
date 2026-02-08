import requests

response = requests.get('https://railway-engine-production.up.railway.app/api/sports/30/picks/player-props?limit=10')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data.get('items', []))} player props")
else:
    print("No player props")
