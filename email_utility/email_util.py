import glob
import logging
import mimetypes
import os
import smtplib
import zipfile
from datetime import datetime
from email.message import EmailMessage

hitlLogger = logging.getLogger("HitlLogger")


def zip_screenshots(screenshots_folder: str, zip_filename: str):
    png_files = glob.glob(os.path.join(screenshots_folder, '*.png'))

    if not png_files:
        # print("⚠️ No screenshots found to zip. Email will not be sent.")
        hitlLogger.info("⚠️ No screenshots found to zip. Email will not be sent.")
        return False

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in png_files:
            zipf.write(file, arcname=os.path.basename(file))
    # print(f"✅ Created zipped file with screenshots at {zip_filename}")
    hitlLogger.info(f"✅ Created zipped file with screenshots at {zip_filename}")
    return True


def send_email_with_zip(
        smtp_server: str,
        smtp_port: int,
        email_user: str,
        email_password: str,
        to_email: str,
        subject: str,
        body: str,
        zip_filename: str
):
    if not os.path.exists(zip_filename):
        # print(f"⚠️ Zip file not found at {zip_filename}. Email not sent.")
        hitlLogger.info(f"⚠️ Zip file not found at {zip_filename}. Email not sent.")
        return

    # Prepare email
    msg = EmailMessage()
    msg["From"] = email_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach zip file
    with open(zip_filename, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename=os.path.basename(zip_filename)
        )

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if email_password:
                server.starttls()
                server.login(email_user, email_password)
            server.send_message(msg)
        hitlLogger.info("📧 Allure Report zipped email successfully sent.")
    except Exception as e:
        # print(f"❌ Error sending email: {e}")
        hitlLogger.info(f"❌ Error sending email: {e}")


def get_timestamped_filename(prefix: str, ext: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{ext}"


def send_email_with_attachments(
        smtp_server: str,
        smtp_port: int,
        email_user: str,
        email_password: str,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: list[str]
):
    msg = EmailMessage()
    msg["From"] = email_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("This is a MIME email. Please view it in HTML.")
    msg.add_alternative(html_body, subtype="html")

    for file_path in attachments:
        if not os.path.exists(file_path):
            continue
        with open(file_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            maintype, subtype = mime_type.split("/") if mime_type else ("application", "octet-stream")
            msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if email_password:
                server.starttls()
                server.login(email_user, email_password)
            server.send_message(msg)
        print("📧 Email with attachments sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
