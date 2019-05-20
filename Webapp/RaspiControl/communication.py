import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for

def send_reset_token(user, method):
    token = user.get_reset_token()

    message = f"""<p>To reset your password, visit the following link:</p>\
\
<p>{url_for('reset_token', token=token, _external=True)}</p>\
\
<p>If you did not make this request then you should consider changing your information for your own protection.</p>
"""
    send_notification(contact=user.email, method="email", subject="Password Reset Request", message=message)


def send_notification(contact, method, subject, message, provider=""):
    gmailsmpt = "smtp.gmail.com"
    msg = MIMEMultipart()
    msg["From"] = os.environ.get("RASPICONTROL_EMAIL")
    msg["Subject"] = subject
    msg["To"] = f"{contact}"
    password = os.environ.get("RASPICONTROL_PASSWORD")
    body = message
    msg.attach(MIMEText(body, "html"))
    server = smtplib.SMTP(gmailsmpt, 587)
    server.starttls()
    server.login(msg["From"], password)
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    server.quit()