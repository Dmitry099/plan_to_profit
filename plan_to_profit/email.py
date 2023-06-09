from threading import Thread

from flask import render_template, current_app
from flask_mail import Mail, Message

mail = Mail()


def send_email_in_thread(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    Thread(target=send_email_in_thread, args=(current_app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        "[Plan To Profit] Reset Your Password",
        sender=current_app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template(
            "email/reset_password.txt", user=user, token=token
        ),
        html_body=render_template(
            "email/reset_password.html", user=user, token=token
        ),
    )
