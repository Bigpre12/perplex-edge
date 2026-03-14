import os
import httpx
import resend
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from database import async_session_maker
from sqlalchemy import select
from models.users import User
from models.brain import ModelPick

resend.api_key = os.environ.get("RESEND_API_KEY", "re_mock_api_key_only")
SENDER_EMAIL = os.environ.get("RESEND_SENDER_EMAIL", "oracle@perplexedge.com")

async def fetch_top_picks(db):
    """Hits the DB to get the Top 3 Highest EV Props"""
    try:
        stmt = select(ModelPick).filter(
            ModelPick.status == "pending",
            ModelPick.ev_percentage > 5
        ).order_by(ModelPick.ev_percentage.desc()).limit(3)
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        print(f"Cron Error Fetching Picks: {e}")
    return []

def generate_email_html(picks, user=None):
    """Builds the HTML String for the Daily Email Report"""
    html_content = f"""
    <div style="font-family: 'Space Grotesk', sans-serif; background-color: #050505; color: #ffffff; padding: 40px; border-radius: 16px;">
        <h1 style="color: #FFD700; margin-bottom: 8px;">Lucrix Oracle: Live Edge Detection</h1>
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 30px;">
            Hey {user.username if user else 'Bettor'}, here are your Top 3 Sharp Action Picks for {datetime.now().strftime('%B %d, %Y')}.
        </p>
    """

    for i, prop in enumerate(picks):
        player_name = prop.player_name
        stat = prop.stat_type
        line = f"O {prop.line}"
        edge = prop.ev_percentage or 0.0
        
        html_content += f"""
        <div style="background-color: #0c1416; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 18px;">{i+1}. {player_name}</h3>
                <span style="background-color: rgba(13, 242, 51, 0.1); color: #0df233; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">
                    {edge:.1f}% Edge
                </span>
            </div>
            <p style="margin: 0; color: #cbd5e1; font-weight: 600;">{stat} &bull; {line} &bull; {prop.sportsbook}</p>
        </div>
        """
        
    html_content += """
        <a href="https://perplexedge.com/slate" style="display: inline-block; background-color: #0df233; color: #000000; font-weight: bold; text-decoration: none; padding: 12px 24px; border-radius: 8px; margin-top: 20px;">
            View Full Institutional Slate
        </a>
    </div>
    """
    
    return html_content

async def send_daily_sharp_report():
    """Triggered by APScheduler to blast the email to Pro users"""
    print(f"[{datetime.now()}] 📧 Running Daily Sharp Email Report...")
    
    async with async_session_maker() as db:
        picks = await fetch_top_picks(db)
        if not picks:
            print("No picks available to send. Aborting email blast.")
            return

        stmt = select(User).filter(User.is_active == True, User.tier.in_(["PRO", "SHARP"]))
        res = await db.execute(stmt)
        users = res.scalars().all()

        for user in users:
            if not user.email:
                continue

            html_body = generate_email_html(picks, user)
            
            try:
                r = resend.Emails.send({
                    "from": SENDER_EMAIL,
                    "to": user.email,
                    "subject": f"🎯 Top Edge Plays for {datetime.now().strftime('%m/%d')}",
                    "html": html_body
                })
                print(f"✅ Daily Sharp Report Sent Successfully to {user.email}! Resend ID: {r.get('id')}")
            except Exception as e:
                print(f"❌ Failed to send Daily Report to {user.email} via Resend: {e}")

# Create the global scheduler
scheduler = AsyncIOScheduler()

def start_email_cron():
    """Boots the APScheduler to run the job daily at 9:00 AM"""
    scheduler.add_job(send_daily_sharp_report, 'cron', hour=9, minute=0)
    scheduler.start()
    print("⏰ Email Cron Scheduler via APScheduler has booted.")
