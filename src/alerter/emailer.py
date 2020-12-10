import logging
import smtplib

from email.message import EmailMessage
from email.utils import formatdate

from alerter.common import Alerter, AlerterFactory


@AlerterFactory.register
class EmailAlerter(Alerter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sender = kwargs.get('sender')
        self.recipients = kwargs.get('recipients')
        self.relay = kwargs.get('relay')

    @classmethod
    def from_args(cls, args):
        sender = args.email[0]
        recipients = args.email
        relay = args.relay
        return cls(sender=sender, recipients=recipients, relay=relay)

    @classmethod
    def from_config(cls, config):
        sender = config['sender']
        recipients = config['recipients']
        relay = config['relay']
        return cls(sender=sender, recipients=recipients, relay=relay)

    @staticmethod
    def get_alerter_type():
        return 'email'

    def __call__(self, **kwargs):
        msg = EmailMessage()

        set_subject = kwargs.get("subject")
        set_content = kwargs.get("content")

        msg.add_header("Date", formatdate())
        msg.set_content(set_content)
        if set_subject:
            msg["Subject"] = set_subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(self.recipients)
        with smtplib.SMTP(self.relay) as s:
            logging.debug(f"sending email: subject: {set_subject}")
            s.send_message(msg)
