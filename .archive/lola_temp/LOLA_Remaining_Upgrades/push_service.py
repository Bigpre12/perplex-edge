# backend/services/push_service.py
# Sends Web Push notifications to subscribers
# pip install pywebpush
import json, os
from pywebpush import webpush, WebPushException
from sqlalchemy.orm import Session
from models import PushSubscription
from typing import Optional

VAPID_PRIVATE = os.getenv('VAPID_PRIVATE_KEY')
VAPID_PUBLIC  = os.getenv('VAPID_PUBLIC_KEY')
VAPID_CLAIMS  = {'sub': f'mailto:{os.getenv("VAPID_EMAIL", "you@yourdomain.com")}'}

def send_push_to_user(user_id: str, title: str, body: str, url: str, db: Session):
    subs = db.query(PushSubscription).filter(PushSubscription.user_id == user_id).all()
    payload = json.dumps({'title': title, 'body': body, 'url': url})
    results = []
    for sub in subs:
        keys = json.loads(sub.keys_json)
        try:
            webpush(
                subscription_info={'endpoint': sub.endpoint, 'keys': keys},
                data=payload,
                vapid_private_key=VAPID_PRIVATE,
                vapid_claims=VAPID_CLAIMS
            )
            results.append({'sub': sub.endpoint[:40], 'status': 'sent'})
        except WebPushException as e:
            if '410' in str(e) or '404' in str(e):
                db.delete(sub)
                db.commit()
            results.append({'sub': sub.endpoint[:40], 'status': 'failed', 'error': str(e)})
    return results

def send_push_to_all(title: str, body: str, url: str, db: Session):
    subs = db.query(PushSubscription).all()
    user_ids = list(set(s.user_id for s in subs))
    sent = 0
    for uid in user_ids:
        results = send_push_to_user(uid, title, body, url, db)
        sent += sum(1 for r in results if r['status'] == 'sent')
    return {'total_sent': sent}

def notify_line_move(player_name: str, stat: str, old_line: float, new_line: float,
                     sharp_side: str, db: Session):
    move = round(abs(new_line - old_line), 1)
    title = f'Line Move: {player_name}'
    body = f'{stat} moved {old_line} → {new_line} ({move} pts) | Sharp: {sharp_side}'
    return send_push_to_all(title, body, '/picks', db)

def notify_injury(player_name: str, status: str, db: Session):
    title = f'Injury Alert: {player_name}'
    body = f'{player_name} is now {status} — check affected props'
    return send_push_to_all(title, body, '/picks', db)
