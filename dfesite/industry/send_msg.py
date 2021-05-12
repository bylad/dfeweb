from django.core.mail import send_mail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

HTTP_LINK = 'https://sift.adm-nao.ru'


def sending(app, news_id, title):
    msg = MIMEMultipart()
    recipients = ['nhaymina@adm-nao.ru', 'btcyrenzhapov@adm-nao.ru']
    # recipients = ['btcyrenzhapov@adm-nao.ru']
    msg['To'] = ', '.join(recipients)
    msg['From'] = 'dfei@adm-nao.ru'
    msg['Subject'] = 'Новые стат.данные'

    body_text = f'Добавлена новость<br><a href="{HTTP_LINK}/{app}/{news_id}/">{title}</a>'

    body = MIMEText(body_text, 'html', 'utf-8')
    msg.attach(body)  # add message body (text or html)

    s = smtplib.SMTP('mail.adm-nao.ru')
    s.sendmail(msg['From'], recipients, msg.as_string())
    s.close()
