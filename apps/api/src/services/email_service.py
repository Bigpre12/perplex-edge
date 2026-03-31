import os
import resend
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Configure Resend with API Key from settings
        api_key = getattr(settings, "RESEND_API_KEY", "")
        if not api_key:
            logger.warning("EmailService: RESEND_API_KEY not configured. Emails will be logged but not sent.")
            resend.api_key = "mock_key"
        else:
            resend.api_key = api_key

    def send_welcome_email(self, user_email: str, username: str):
        """Send a premium welcome email to new users."""
        if resend.api_key == "mock_key":
            logger.info(f"MOCK EMAIL: Welcome email would be sent to {user_email}")
            return

        try:
            params = {
                "from": f"Perplex Edge <{os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')}>",
                "to": [user_email],
                "subject": "Welcome to Perplex Edge Neural Engine!",
                "html": f"""
                    <div style="font-family: sans-serif; background: #050505; color: #fff; padding: 40px; border-radius: 20px; border: 1px solid #1e293b;">
                        <h1 style="color: #3b82f6; margin-bottom: 20px;">Welcome to the Edge, {username}!</h1>
                        <p style="font-size: 16px; color: #94a3b8; line-height: 1.6;">The neural engine is active. You have successfully integrated with the Perplex Edge data stream.</p>
                        <div style="margin-top: 30px;">
                            <a href="{settings.FRONTEND_URL}" style="background: #2563eb; color: #fff; padding: 14px 28px; text-decoration: none; border-radius: 12px; font-weight: bold; display: inline-block;">Launch Neural Dashboard</a>
                        </div>
                        <p style="margin-top: 30px; font-size: 12px; color: #475569;">© 2026 Perplex Edge. Analytical intelligence for the institutional bettor.</p>
                    </div>
                """
            }
            resend.Emails.send(params)
            logger.info(f"EmailService: Sent welcome email to {user_email}")
        except Exception as e:
            logger.error(f"EmailService: Failed to send welcome email to {user_email}: {e}")

    def send_password_reset_email(self, user_email: str, token: str):
        """Send a password reset link to the user."""
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        if resend.api_key == "mock_key":
            logger.info(f"SIMULATION MODE: Password reset link for {user_email}: {reset_link}")
            return

        try:
            params = {
                "from": f"Perplex Edge Auth <{os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')}>",
                "to": [user_email],
                "subject": "Neural Access: Reset Your Password",
                "html": f"""
                    <div style="font-family: sans-serif; background: #050505; color: #fff; padding: 40px; border-radius: 20px; border: 1px solid #1e293b;">
                        <h2 style="color: #3b82f6; margin-bottom: 20px;">Neural Access Reset</h2>
                        <p style="font-size: 16px; color: #94a3b8; line-height: 1.6;">We received a request to recalibrate your neural access credentials. Click below to continue.</p>
                        <div style="margin-top: 30px;">
                            <a href="{reset_link}" style="background: #2563eb; color: #fff; padding: 14px 28px; text-decoration: none; border-radius: 12px; font-weight: bold; display: inline-block;">Recalibrate Password</a>
                        </div>
                        <p style="margin-top: 20px; font-size: 12px; color: #475569;">This link will expire in 60 minutes for security protocols.</p>
                    </div>
                """
            }
            resend.Emails.send(params)
            logger.info(f"EmailService: Sent reset link to {user_email}")
        except Exception as e:
            logger.error(f"EmailService: Failed to send reset link to {user_email}: {e}")

email_service = EmailService()
