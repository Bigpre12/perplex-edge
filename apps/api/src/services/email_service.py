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
                "from": "Lucrix <onboarding@resend.dev>", # Update with verified domain in production
                "to": [user_email],
                "subject": "Welcome to Perplex Edge Neural Engine!",
                "html": f"""
                    <div style="font-family: sans-serif; background: #050505; color: #fff; padding: 40px; border-radius: 20px;">
                        <h1 style="color: #3b82f6;">Welcome, {username}!</h1>
                        <p style="font-size: 16px; color: #aaa;">Your edge starts now. You've successfully integrated with the Perplex Edge neural engine.</p>
                        <div style="margin-top: 30px;">
                            <a href="{settings.FRONTEND_URL}" style="background: #2563eb; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 12px; font-weight: bold;">Launch Dashboard</a>
                        </div>
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
            logger.info(f"MOCK EMAIL: Password reset link for {user_email}: {reset_link}")
            return

        try:
            params = {
                "from": "Lucrix Auth <auth@resend.dev>",
                "to": [user_email],
                "subject": "Reset Your Perplex Edge Password",
                "html": f"""
                    <div style="font-family: sans-serif; background: #050505; color: #fff; padding: 40px; border-radius: 20px;">
                        <h2 style="color: #3b82f6;">Password Reset Request</h2>
                        <p style="font-size: 16px; color: #aaa;">We received a request to reset your password. Click the button below to proceed. This link expires in 1 hour.</p>
                        <div style="margin-top: 30px;">
                            <a href="{reset_link}" style="background: #2563eb; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 12px; font-weight: bold;">Reset Password</a>
                        </div>
                        <p style="margin-top: 20px; font-size: 12px; color: #555;">If you didn't request this, you can safely ignore this email.</p>
                    </div>
                """
            }
            resend.Emails.send(params)
            logger.info(f"EmailService: Sent reset link to {user_email}")
        except Exception as e:
            logger.error(f"EmailService: Failed to send reset link to {user_email}: {e}")

email_service = EmailService()
