from flask import render_template, current_app
from flask_mail import Message
from . import  mail



def send_email(to, subject, template, **kwargs):
    msg=Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    msg.body=render_template(template+'.txt', **kwargs)
    # msg.html=render_template(template+'.html', **kwargs )
    mail.send(msg)