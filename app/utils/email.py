# app/utils/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to: str, subject: str, body: str):
    """
    Send an HTML email using Gmail SMTP.
    Make sure to enable 'App Passwords' for your Gmail account.
    """
    sender_email = "jagadeeshkadavakuti5@gmail.com"       # 🔹 Replace with your Gmail
    sender_password = "Sivaroyal@123"      # 🔹 Replace with your App Password

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to, msg.as_string())
            print(f"✅ Email sent successfully to {to}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise e
