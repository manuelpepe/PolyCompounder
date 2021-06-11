import ssl
import logging
import smtplib
import traceback
import time 

from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PolyCompounder.config import ALERTS_ON, ALERTS_ADDRESS, ALERTS_HOST, ALERTS_PASSWORD, ALERTS_PORT, ALERTS_RECIPIENT


logger = logging.getLogger("PolyCompounder.alert")
SSL_CONTEXT = ssl.create_default_context()


@contextmanager
def smtp():
    with smtplib.SMTP(ALERTS_HOST, port=ALERTS_PORT) as _server:
        _server.starttls(context=SSL_CONTEXT)
        _server.login(ALERTS_ADDRESS, ALERTS_PASSWORD)
        yield _server


def alert_exception(exception):
    content = "Error on PolyCompounder:\n\n"
    content += ''.join(traceback.format_tb(exception.__traceback__))
    content += f"\n{type(exception).__name__}: {exception}"
    send_email(content)


def send_email(content):
    if ALERTS_ON:
        with smtp() as _server:
            msg = MIMEMultipart()
            msg['From'] = ALERTS_ADDRESS
            msg['To'] = ALERTS_RECIPIENT
            msg['Subject'] = "Error on PolyCompounder"
            msg.attach(MIMEText(content, 'plain'))
            _server.send_message(msg)
