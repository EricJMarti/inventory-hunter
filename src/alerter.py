# import logging
import sys
import smtplib
import traceback

from email.message import EmailMessage
from email.utils import formatdate

import requests

from loguru import logger as logging


class AlerterBase:
    def __init__(self, *args, **kwargs):
        pass

    def _notification_function(self, **kwargs):
        pass

    def __call__(self, content, **kwargs):
        self._notification_function(content=content, **kwargs)


class AlerterTest(AlerterBase):
    def __init__(self, *args, **kwargs):
        logging.debug(f"dropped args: {args}")
        logging.debug(f"dropped kwargs: {kwargs}")
        super().__init__(args, **kwargs)

    def _notification_function(self, **kwargs):
        logging.debug(f"notification function kwargs: {kwargs}")


class DiscordAlerter(AlerterBase):
    def __init__(self, args):
        self._webhook_url = args.webhook_url
        super().__init__(args)

    def _notification_function(self, **kwargs):
        _discord_embed_generated = {
            "content": None,
            "embeds": [
                {"title": "Alert", "description": kwargs.get("content"), "color": 5832569}
            ],
            "username": "Inventory Hunter",
            "avatar_url": "https://i.imgur.com/X1o5j0N.jpeg",
        }
        try:
            logging.debug(f"Discord Webhook URL: {self._webhook_url}")
            send_request = requests.post(
                self._webhook_url,
                json=_discord_embed_generated,
            )
            if send_request.status_code != 204:
                logging.error(
                    f"There was an issue sending to discord due to an invalid status code back -> {send_request.status_code}"
                )
        except Exception:
            logging.error(
                f"Issue with sending webhook to discord. {traceback.format_exc()}"
            )


class EmailAlerter(AlerterBase):
    def __init__(self, args):
        self.sender = args.email[0]
        self.recipients = args.email
        self.relat = args.relay
        super().__init__(args)

    def _notification_function(self, **kwargs):
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
