import logging
import sched
import smtplib
import sys

from email.message import EmailMessage
from scraper import Scraper


class Alerter:
    def __init__(self, args):
        self.email = args.email
        self.relay = args.relay

        # self('Testing relay', 'You can delete this message.')

    def __call__(self, subject, content):
        msg = EmailMessage()
        msg.set_content(content)
        if subject:
            msg['Subject'] = subject
        msg['From'] = self.email
        msg['To'] = self.email
        s = smtplib.SMTP(self.relay)
        logging.debug(f'sending email with subject: {subject}')
        s.send_message(msg)
        s.quit()


class Engine:
    def __init__(self, args, config):
        self.alerter = Alerter(args)
        self.refresh_interval = config.refresh_interval
        self.scheduler = sched.scheduler()
        self.scrapers = [Scraper(url, self.refresh_interval) for url in config.urls]
        for s in self.scrapers:
            self.schedule(s)

    def run(self):
        self.scheduler.run(blocking=True)

    def schedule(self, s):
        if self.scheduler.queue:
            t = self.scheduler.queue[-1].time + self.refresh_interval
            self.scheduler.enterabs(t, 1, Engine.tick, (self, s))
        else:
            self.scheduler.enter(self.refresh_interval, 1, Engine.tick, (self, s))

    def tick(self, s):
        result = s.scrape()

        if result is None:
            logging.error(f'{s.name}: scrape failed')

        elif result and s.in_stock_on_last_scrape:
            logging.info(f'{s.name}: still in stock')

        elif result:
            logging.info(f'{s.name}: now in stock!')
            self.alerter(result.alert_subject, result.alert_content)
            s.in_stock_on_last_scrape = True

        elif result.has_phrase('are you a human'):
            logging.error(f'{s.name}: got "are you a human" prompt')
            self.alerter('Something went wrong',
                         f'You need to answer this CAPTCHA and restart this script: {result.url}')
            sys.exit(1)

        else:
            logging.info(f'{s.name}: not in stock')
            s.in_stock_on_last_scrape = False

        return self.schedule(s)


def hunt(args, config):
    engine = Engine(args, config)
    engine.run()
