# app/utils/email.py

import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
GMAIL_EMAIL = "jagadeeshkadavakuti5@gmail.com"  # 🔹 Replace with your Gmail
GMAIL_PASSWORD = "Sivaroyal@123"  # 🔹 Replace with your App Password

# Zepto Mail Configuration
ZEPTO_API_KEY = os.getenv("ZEPTO_API_KEY", "your_zepto_api_key_here")  # 🔹 Set in .env file
ZEPTO_API_URL = "https://api.zeptomail.com/v1.1/email/send"

def send_email_gmail(to: str, subject: str, body: str):
    """
    Send an HTML email using Gmail SMTP.
    Make sure to enable 'App Passwords' for your Gmail account.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_EMAIL
    msg["To"] = to
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            server.sendmail(GMAIL_EMAIL, to, msg.as_string())
            print(f"✅ Email sent successfully to {to} via Gmail")
            return True
    except Exception as e:
        print(f"❌ Failed to send email via Gmail: {e}")
        return False


def send_email_zepto(to: str, subject: str, body: str, from_name: str = "TravelNudge"):
    """
    Send an HTML email using Zepto Mail API.
    Requires ZEPTO_API_KEY to be set in environment variables.
    """
    headers = {
        "Authorization": f"{ZEPTO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": {
            "address": GMAIL_EMAIL,
            "name": from_name
        },
        "to": [
            {
                "email_address": {
                    "address": to,
                    "name": to.split("@")[0]
                }
            }
        ],
        "subject": subject,
        "htmlbody": body
    }

    try:
        response = requests.post(ZEPTO_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Email sent successfully to {to} via Zepto Mail")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send email via Zepto Mail: {e}")
        return False


def send_email(to: str, subject: str, body: str, use_zepto: bool = False):
    """
    Send an HTML email using either Gmail or Zepto Mail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email HTML body
        use_zepto: If True, use Zepto Mail; if False, use Gmail SMTP
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if use_zepto:
        return send_email_zepto(to, subject, body)
    else:
        return send_email_gmail(to, subject, body)


def send_password_reset_email(to: str, reset_token: str, user_name: Optional[str] = None):
    """
    Send password reset email to user using Zepto Mail.
    
    Args:
        to: Recipient email address
        reset_token: Password reset token/link
        user_name: User's name for personalization
    """
    user_display = user_name if user_name else "User"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #2c3e50; color: #fff; padding: 20px; border-radius: 5px 5px 0 0; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
            .button {{ background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
            .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧳 TravelNudge - Password Reset</h1>
            </div>
            <div class="content">
                <p>Hi {user_display},</p>
                <p>We received a request to reset your TravelNudge account password. Click the button below to create a new password:</p>
                
                <center>
                    <a href="{reset_token}" class="button">Reset Your Password</a>
                </center>
                
                <p>Or copy this link in your browser:</p>
                <p><code>{reset_token}</code></p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> This link will expire in 1 hour. If you didn't request this password reset, please ignore this email.
                </div>
                
                <p>Best regards,<br>The TravelNudge Team</p>
            </div>
            <div class="footer">
                <p>© 2025 TravelNudge. All rights reserved.</p>
                <p>If you have any questions, please contact us at support@travelnudge.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    subject = "🔐 Reset Your TravelNudge Password"
    return send_email_zepto(to, subject, html_body)
