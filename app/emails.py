from flask import render_template, current_app
from flask_mail import Message
from app import app, mail
from threading import Thread

def async(f):
    def wrapper(*args, **kwargs):
        try:
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
        except Exception as e:
            print(e)
    return wrapper

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body=text_body
    msg.html=html_body
    send_async_email(app, msg)   

def follower_notification(follower, followed):
    send_email('[microblog] %s is now following you!' % follower.nickname,
        current_app.config['ADMINS'][0],
        [followed.email],
        render_template('follower_email.txt', followed=followed, follower=follower),
        render_template('follower_email.html', followed=followed, follower=follower))
