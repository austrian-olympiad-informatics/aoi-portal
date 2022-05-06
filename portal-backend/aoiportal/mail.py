from flask import render_template
from flask_mail import Mail, Message

mail = Mail()


def send_email(to: str, subject: str, content_html: str) -> None:
    msg = Message(
        subject=subject,
        recipients=[to],
        html=render_template("mail_template.html", content=content_html),
    )
    mail.send(msg)
