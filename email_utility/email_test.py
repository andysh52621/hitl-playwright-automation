import smtplib
from email.message import EmailMessage

# === CONFIGURE THESE ===
SMTP_SERVER = "mailman.corp.vizientinc.com"
SMTP_PORT = 25
EMAIL_USER = "alertmanager@vizientinc.com"
EMAIL_PASSWORD = ""  # Leave empty if unauthenticated
TO_EMAIL = "andy.sharma@vizientinc.com"

# === Compose Email ===
msg = EmailMessage()
msg["From"] = EMAIL_USER
msg["To"] = TO_EMAIL
msg["Subject"] = "📧 SMTP Email Test - HITL Automation"
msg.set_content("This is a test email sent from the email_test.py script.\n\nIf you received this, SMTP is working!")

# === Send Email ===
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        print(f"✅ Connected to SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        if EMAIL_PASSWORD:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
