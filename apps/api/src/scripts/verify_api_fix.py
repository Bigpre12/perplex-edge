import asyncio
import httpx
import json

async def check_api():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get("http://localhost:8000/api/immediate/working-player-props?sport_id=30&limit=1")
            if r.status_code == 200:
                data = r.json()
                print(f"Source: {data.get('source')}")
                item = data["items"][0]
                print(f"Player: {item.get('player_name')}")
                print(f"Teams:  {item.get('away_team')} @ {item.get('home_team')}")
                
                rec = item.get('recommendation')
                print(f"Rec type: {type(rec)}")
                if rec:
                    print(f"Reason: {rec.get('reason')}")
                
                over = item.get('best_over')
                print(f"Over type: {type(over)}")
                if over:
                    print(f"Over:   {over.get('line')} (@{over.get('odds')})")
                
                under = item.get('best_under')
                print(f"Under type: {type(under)}")
                if under:
                    print(f"Under:  {under.get('line')} (@{under.get('odds')})")
            else:
                print(f"Status: {r.status_code}")
                print(r.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_api())
