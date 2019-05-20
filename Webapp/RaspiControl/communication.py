import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for

class CommunicationSending():
    def __init__(self, contact, subject, user=None):
        self.user = user
        self.contact = contact
        self.subject = subject
        self.message = ""

    def send_reset_token(self):
        token = self.user.get_reset_token()

        self.message = f"""<p>To reset your password, visit the following link:</p>\
    \
    <p>{url_for('reset_token', token=token, _external=True)}</p>\
    \
    <p>If you did not make this request then you should consider changing your information for your own protection.</p>
    """
        self.send_email()


    def send_email(self):
        gmailsmpt = "smtp.gmail.com"
        msg = MIMEMultipart()
        msg["From"] = os.environ.get("RASPICONTROL_EMAIL")
        msg["Subject"] = self.subject
        msg["To"] = f"{self.contact}"
        password = os.environ.get("RASPICONTROL_PASSWORD")
        body = self.message
        msg.attach(MIMEText(body, "html"))
        server = smtplib.SMTP(gmailsmpt, 587)
        server.starttls()
        server.login(msg["From"], password)
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.quit()