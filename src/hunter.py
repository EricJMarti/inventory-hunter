import logging
import sched
import smtplib
import sys

from email.message import EmailMessage
from email.utils import formatdate
from scraper import Scraper

from alerter import EmailAlerter, DiscordAlerter

class Engine:
    def __init__(self, args, config, driver):

        alert_types = {
            "email": EmailAlerter,
            "discord": DiscordAlerter
        }
        self.alerter = alert_types[args.alerter_type](args)
        logging.debug(f"selected alerter: {args.alerter_type} -> {self.alerter}")
    
        self.refresh_interval = config.refresh_interval
        self.max_price = config.max_price
        self.scheduler = sched.scheduler()
        self.scrapers = [Scraper(driver, url) for url in config.urls]
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
        else:
            self.process_scrape_result(s, result)

        return self.schedule(s)

    def process_scrape_result(self, s, result):
        currently_in_stock = bool(result)
        current_price = result.price

        if currently_in_stock and s.in_stock_on_last_scrape:

            # if no pricing is available, we'll assume the price hasn't changed
            if current_price is None or s.price_on_last_scrape is None:
                logging.info(f'{s.name}: still in stock')

            # is the current price the same as the last price? (most likely yes)
            elif current_price == s.price_on_last_scrape:
                logging.info(f'{s.name}: still in stock at the same price')

            # has the price gone down?
            elif current_price < s.price_on_last_scrape:

                if self.max_price is None or current_price <= self.max_price:
                    self.send_alert(s, result, f'now in stock at {current_price}!')
                else:
                    logging.info(f'{s.name}: now in stock at {current_price}... still too expensive')

            else:
                logging.info(f'{s.name}: now in stock at {current_price}... more expensive than before :(')

        elif currently_in_stock and not s.in_stock_on_last_scrape:

            # if no pricing is available, we'll assume the price is low enough
            if current_price is None:
                self.send_alert(s, result, 'now in stock!')

            # is the current price low enough?
            elif self.max_price is None or current_price <= self.max_price:
                self.send_alert(s, result, f'now in stock at {current_price}!')

            else:
                logging.info(f'{s.name}: now in stock at {current_price}... too expensive')

        elif not currently_in_stock and result.has_phrase('are you a human'):

            logging.error(f'{s.name}: got "are you a human" prompt')
            self.alerter('Something went wrong',
                         f'You need to answer this CAPTCHA and restart this script: {result.url}')
            sys.exit(1)

        else:
            logging.info(f'{s.name}: not in stock')

        # cache current state
        s.in_stock_on_last_scrape = currently_in_stock
        s.price_on_last_scrape = current_price

    def send_alert(self, s, result, reason):
        logging.info(f'{s.name}: {reason}')
        self.alerter(subject=result.alert_subject, content=result.alert_content)


def hunt(args, config, driver):
    engine = Engine(args, config, driver)
    engine.run()
