import logging
import requests
import traceback

from alerter.common import Alerter, AlerterFactory


@AlerterFactory.register
class SlackAlerter(Alerter):
    def __init__(self, args):
        self.webhook_url = args.webhook_url
        super().__init__(args)

    @classmethod
    def from_args(cls, args):
        webhook_url = args.webhook_url
        return cls(webhook_url=webhook_url)

    @classmethod
    def from_config(cls, config):
        webhook_url = config['webhook_url']
        return cls(webhook_url=webhook_url)

    @staticmethod
    def get_alerter_type():
        return 'slack'

    def __call__(self, **kwargs):
        _slack_webhook_generated = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Inventory Hunter* :mega:"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": kwargs.get("content")
                    }
                }
            ]
        }
        try:
            logging.debug(f"Slack Webhook URL: {self.webhook_url}")
            send_request = requests.post(
                self.webhook_url,
                json=_slack_webhook_generated,
            )
            if send_request.status_code != 200 and send_request.text == "ok":
                logging.error(
                    f"There was an issue sending to slack due to an invalid request: {send_request.status_code} -> {send_request.text}"
                )
        except Exception:
            logging.error(
                f"Issue with sending webhook to slack. {traceback.format_exc()}"
            )
