from celery import shared_task
from Innotter.aws import ses
from Innotter.settings import AWS


@shared_task
def send_mail_to_followers(post_content, page_name, followers_mails):
    if followers_mails:
        ses.verify_email_identity(EmailAddress=AWS['AWS_EMAIL_SOURCE'])
        ses.send_email(
            Destination={'ToAddresses': followers_mails},
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': post_content,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': 'New post on ' + page_name + ' page.',
                },
            },
            Source=AWS['AWS_EMAIL_SOURCE'],
        )
