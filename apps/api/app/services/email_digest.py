import os
import resend
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, PlayerProp
from datetime import date

resend.api_key = os.getenv("RESEND_API_KEY", "re_mock_key_123")

def generate_html_digest(user, top_props):
    props_html = "".join([
        f"<li><b>{p.player_name}</b> O {p.line} {p.prop_type} (Edge: {p.edge_score}%)</li>"
        for p in top_props
    ])
    return f"""
    <html>
    <body>
        <h2>Your Daily Edge Digest 🎯</h2>
        <p>Hey {user.username or 'Bettor'}, here are the top +EV plays for today:</p>
        <ul>{props_html}</ul>
        <br/>
        <p>Good luck tonight!<br/>- The Perplex Engine Team</p>
    </body>
    </html>
    """

def send_daily_digest(db: Session = None):
    print("Starting Daily Email Digest Job...")
    if not db:
        db = SessionLocal()
        
    try:
        users = db.query(User).filter(User.is_active == True, User.tier.in_(["PRO", "SHARP"])).all()
        top_props = db.query(PlayerProp).filter(
            PlayerProp.is_settled == False,
            PlayerProp.edge_score > 5
        ).order_by(PlayerProp.edge_score.desc()).limit(3).all()

        if not top_props:
            print("No significant edges today. Skipping emails.")
            return

        for user in users:
            if not user.email:
                continue
                
            html_content = generate_html_digest(user, top_props)
            
            try:
                r = resend.Emails.send({
                    "from": "edges@perplex.com",
                    "to": user.email,
                    "subject": f"🔥 Top {len(top_props)} Edges for {date.today().strftime('%b %d')}",
                    "html": html_content
                })
                print(f"Sent digest to {user.email}")
            except Exception as e:
                print(f"Failed to send email to {user.email}: {e}")
                
    finally:
        db.close()
        print("Daily Email Digest Job Complete.")
