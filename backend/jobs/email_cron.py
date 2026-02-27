import os
import httpx
import resend
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Initialize Resend
resend.api_key = os.environ.get("RESEND_API_KEY", "re_mock_api_key_only")
SENDER_EMAIL = os.environ.get("RESEND_SENDER_EMAIL", "oracle@perplexedge.com")

async def fetch_top_picks():
    """Hits the local API to get the Top 3 Highest EV Props"""
    port = os.environ.get("PORT", "8000")
    internal_url = f"http://localhost:{port}/immediate/working-player-props?limit=3"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(internal_url)
            if res.status_code == 200:
                data = res.json()
                if data and len(data) > 0:
                    return data
    except Exception as e:
        print(f"Cron Error Fetching Picks: {e}")
    return []

def generate_email_html(picks):
    """Builds the HTML String for the Daily Email Report"""
    html_content = f"""
    <div style="font-family: 'Space Grotesk', sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 16px;">
        <h1 style="color: #0df233; margin-bottom: 8px;">Perplex Oracle: Live Edge Detection</h1>
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 30px;">
            Here are your Top 3 Sharp Action Picks for {datetime.now().strftime('%B %d, %Y')}.
        </p>
    """

    for i, prop in enumerate(picks):
        player_name = prop.get("player_name") or prop.get("player", {}).get("name", "Unknown")
        stat = prop.get("stat_type") or prop.get("market", {}).get("stat_type", "Prop")
        line = f"{'Over' if prop.get('side') == 'over' else 'Under'} {prop.get('line_value') or prop.get('line')}"
        edge = prop.get("edge", 0) * 100
        
        html_content += f"""
        <div style="background-color: #0c1416; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 18px;">{i+1}. {player_name}</h3>
                <span style="background-color: rgba(13, 242, 51, 0.1); color: #0df233; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">
                    {edge:.1f}% Edge
                </span>
            </div>
            <p style="margin: 0; color: #cbd5e1; font-weight: 600;">{stat} &bull; {line} &bull; {prop.get('sportsbook', 'Sharp')}</p>
        </div>
        """
        
    html_content += """
        <a href="https://perplexedge.com/institutional/strategy-lab" style="display: inline-block; background-color: #0df233; color: #000000; font-weight: bold; text-decoration: none; padding: 12px 24px; border-radius: 8px; margin-top: 20px;">
            View Full Institutional Slate
        </a>
    </div>
    """
    
    return html_content

async def send_daily_sharp_report():
    """Triggered by APScheduler to blast the email to Pro users"""
    print(f"[{datetime.now()}] 📧 Running Daily Sharp Email Report...")
    
    picks = await fetch_top_picks()
    if not picks:
        print("No picks available to send. Aborting email blast.")
        return
        
    html_body = generate_email_html(picks)
    
    # In a full production environment, we would iterate over a Supabase query of PRO users.
    # For now, we simulate broadcasting to an admin testing list.
    subscribers = ["test_user_1@example.com", "test_user_2@example.com"]
    
    try:
        r = resend.Emails.send({
            "from": SENDER_EMAIL,
            "to": subscribers,
            "subject": f"🎯 Top Edge Plays for {datetime.now().strftime('%m/%d')}",
            "html": html_body
        })
        print(f"✅ Daily Sharp Report Sent Successfully! Resend ID: {r.get('id')}")
    except Exception as e:
        print(f"❌ Failed to send Daily Report via Resend: {e}")

# Create the global scheduler
scheduler = AsyncIOScheduler()

def start_email_cron():
    """Boots the APScheduler to run the job daily at 9:00 AM"""
    # Using minute testing interval here for dev visibility, normally `hour=9`
    scheduler.add_job(send_daily_sharp_report, 'cron', hour=9, minute=0)
    scheduler.start()
    print("⏰ Email Cron Scheduler via APScheduler has booted.")
