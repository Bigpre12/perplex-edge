import requests
response = requests.get('https://railway-engine-production.up.railway.app/api/sports')
print(response.json())
