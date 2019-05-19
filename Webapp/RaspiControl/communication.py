import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_notification(contact, method, subject, message, provider=""):
    gmailsmpt = "smtp.gmail.com"
    msg = MIMEMultipart()
    msg["From"] = os.environ.get("RASPICONTROL_EMAIL")
    if method == "email":
        msg["To"] = f"{contact}"
    elif method == "text":
        msg["To"] = f"{contact}{provider}"
    password = os.environ.get("RASPICONTROL_PASSWORD")
    msg["Subject"] = subject
    body = message
    msg.attach(MIMEText(body, "html"))
    server = smtplib.SMTP(gmailsmpt, 587)
    server.starttls()
    server.login(msg["From"], password)
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    server.quit()