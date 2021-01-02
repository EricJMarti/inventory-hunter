import logging
import traceback

# from pushover import Client

from alerter.common import Alerter, AlerterFactory


@AlerterFactory.register
class PushoverAlerter(Alerter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_token = kwargs.get('api_token')
        self.user_key = kwargs.get('user_key')

    @classmethod
    def from_args(cls, args):
        api_token = args.api_token
        user_key = args.user_key
        return cls(api_token=api_token, user_key=user_key)

    @classmethod
    def from_config(cls, config):
        api_token = config['api_token']
        user_key = config['user_key']
        return cls(api_token=api_token, user_key=user_key)

    @staticmethod
    def get_alerter_type():
        return 'pushover'

    def __call__(self, **kwargs):
        title = kwargs.get("subject")
        message = kwargs.get("content")
        try:
            logging.debug(f"Pushover user key: {self.user_key}")
            # client = Client(self.user_key, api_token=self.api_token)
            # client.send_message(message, title=title)
        except Exception:
            logging.error(
                f"Issue with sending message to Pushover. {traceback.format_exc()}"
            )
