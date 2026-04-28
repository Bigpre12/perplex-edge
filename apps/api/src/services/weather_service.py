# backend/services/weather_service.py
# Weather and venue impact for NFL/MLB props
import httpx, os
from services.api_telemetry import InstrumentedAsyncClient
from typing import Optional

OWM_KEY = os.getenv('OPENWEATHER_API_KEY')

DOME_STADIUMS = {
    'DAL': True, 'NO': True, 'ATL': True, 'LV': True, 'DET': True,
    'MIN': True, 'ARI': True, 'HOU': True, 'IND': True, 'STL': True
}

STADIUM_COORDS = {
    'BUF': (42.7738, -78.7870), 'CHI': (41.8623, -87.6167),
    'KC': (39.0489, -94.4839), 'GB': (44.5013, -88.0622),
    'NE': (42.0909, -71.2643), 'NYG': (40.8135, -74.0745),
    'NYJ': (40.8135, -74.0745), 'PHI': (39.9008, -75.1675),
    'PIT': (40.4468, -80.0158), 'SF': (37.4032, -121.9698),
    'SEA': (47.5952, -122.3316), 'LAR': (33.9535, -118.3392),
    'LAC': (33.9535, -118.3392), 'MIA': (25.9580, -80.2389),
    'TB': (27.9759, -82.5033), 'CAR': (35.2258, -80.8528),
    'TEN': (36.1665, -86.7713), 'JAX': (30.3239, -81.6373),
    'CIN': (39.0954, -84.5160), 'CLE': (41.5061, -81.6995),
    'BAL': (39.2780, -76.6228), 'DEN': (39.7439, -105.0201),
    'OAK': (37.7516, -122.2005), 'WAS': (38.9078, -76.8645)
}

class WeatherService:
    def __init__(self):
        self.owm_key = os.getenv('OPENWEATHER_API_KEY')

    async def get_game_weather(self, team_abbr: str) -> dict:
        if DOME_STADIUMS.get(team_abbr):
            return {'is_dome': True, 'weather_impact': 'NONE', 'conditions': 'Indoor'}
        coords = STADIUM_COORDS.get(team_abbr)
        if not coords:
            return {'is_dome': False, 'weather_impact': 'UNKNOWN', 'conditions': 'Data unavailable'}
        
        lat, lon = coords
        if not self.owm_key:
            return {'error': 'Weather API Key missing', 'is_dome': False}
            
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.owm_key}&units=imperial'
        try:
            async with InstrumentedAsyncClient(provider="openweathermap", timeout=5) as c:
                r = await c.get(url)
                if r.status_code != 200:
                    return {'error': 'Weather API unavailable'}
                data = r.json()
                
            wind_mph = round(data['wind']['speed'], 1)
            temp_f = round(data['main']['temp'], 1)
            conditions = data['weather'][0]['main']
            
            impact_factors = []
            impact_level = 'LOW'
            
            if wind_mph >= 20:
                impact_factors.append(f'High wind ({wind_mph} mph) — reduces passing/kicking')
                impact_level = 'HIGH' if wind_mph >= 30 else 'MODERATE'
            if temp_f <= 20:
                impact_factors.append(f'Extreme cold ({temp_f}F) — reduces scoring')
                impact_level = 'HIGH'
            if conditions in ['Rain', 'Snow', 'Drizzle', 'Thunderstorm']:
                impact_factors.append(f'{conditions} — reduces passing/rushing efficiency')
                impact_level = 'HIGH' if conditions in ['Snow', 'Thunderstorm'] else 'MODERATE'
                
            return {
                'is_dome': False,
                'team': team_abbr,
                'temperature_f': temp_f,
                'wind_mph': wind_mph,
                'conditions': conditions,
                'weather_impact': impact_level,
                'impact_factors': impact_factors,
                'prop_advice': '; '.join(impact_factors) if impact_factors else 'No significant weather impact'
            }
        except Exception as e:
            return {'error': f'Weather service error: {str(e)}'}

weather_service = WeatherService()
get_game_weather = weather_service.get_game_weather
