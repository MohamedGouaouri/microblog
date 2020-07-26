from flask import render_template
from flask_mail import Message
from app import mail
from app import app
from app.forms import User


def send_email(subject, sender, recipients, text_body,  html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
	token = user.get_reset_password_token()
	send_email('[Microblog] Reset Your Password',
				sender=app.config['ADMINS'],
				recipients=user.email,
				text_body=render_template('email/reset_password_email.txt', user=user, token=token),
				html_body=render_template('email/reset_password_email.html', user=usern, token=token)
	)