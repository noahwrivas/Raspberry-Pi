import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "Testingsenderemailpython.gmail.com"  # Enter your address
receiver_email = "noahwar97@me.com"  # Enter receiver address
password = "Testingpassword"
message = f"""
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)