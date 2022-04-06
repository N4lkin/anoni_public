from anoni.celery import app
from django.core.mail import send_mail

@app.task
def send_mail_for_registration_user(user_email, uuid_link):
    send_mail(
        'AnonI confirmation link',
        "Hi! You try register on AnonI.com\n"
        "If the request was not sent by you please ignore this message\n"
        f"Your verification link: 127.0.0.1:8000/profile/register/{uuid_link}/",
        'anonicorporation@gmail.com',
        [user_email],
        fail_silently=False,
    )

@app.task
def send_mail_for_restore_user_password(user_email, restore_password_uuid):
    send_mail(
        'AnonI restore password',
        "Hi! Your link for restore password on AnonI.com\n"
        "If the request was not sent by you please ignore this message\n"
        f"Your restore password link: 127.0.0.1:8000/profile/reset/{restore_password_uuid}",
        'anonicorporation@gmail.com',
        [user_email],
        fail_silently=False
    )
