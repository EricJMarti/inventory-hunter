import logging
import random
import sched
import sys

from alerter import EmailAlerter, DiscordAlerter, SlackAlerter, TelegramAlerter


random.seed()


class Engine:
    def __init__(self, args, config, scrapers):

        alert_types = {
            "email": EmailAlerter,
            "discord": DiscordAlerter,
            "slack": SlackAlerter,
            "telegram": TelegramAlerter
        }
        self.alerter = alert_types[args.alerter_type](args)
        logging.debug(f"selected alerter: {args.alerter_type} -> {self.alerter}")

        self.refresh_interval = config.refresh_interval
        self.max_price = config.max_price
        self.scheduler = sched.scheduler()
        for s in scrapers:
            self.schedule(s)

    def run(self):
        self.scheduler.run(blocking=True)

    def schedule(self, s):
        time_delta = self.refresh_interval

        # semi-random intervals throw off some web scraping defenses
        time_delta *= random.randint(100, 120) / 100.0

        if self.scheduler.queue:
            t = self.scheduler.queue[-1].time + time_delta
            self.scheduler.enterabs(t, 1, Engine.tick, (self, s))
        else:
            self.scheduler.enter(time_delta, 1, Engine.tick, (self, s))

    def tick(self, s):
        result = s.scrape()

        if result is None:
            s.logger.error('scrape failed')
        else:
            self.process_scrape_result(s, result)

        return self.schedule(s)

    def process_scrape_result(self, s, result):
        currently_in_stock = bool(result)
        previously_in_stock = result.previously_in_stock
        current_price = result.price
        last_price = result.last_price

        if currently_in_stock and previously_in_stock:

            # if no pricing is available, we'll assume the price hasn't changed
            if current_price is None or last_price is None:
                s.logger.info('still in stock')

            # is the current price the same as the last price? (most likely yes)
            elif current_price == last_price:
                s.logger.info('still in stock at the same price')

            # has the price gone down?
            elif current_price < last_price:

                if self.max_price is None or current_price <= self.max_price:
                    self.send_alert(s, result, f'now in stock at {current_price}!')
                else:
                    s.logger.info(f'now in stock at {current_price}... still too expensive')

            else:
                s.logger.info(f'now in stock at {current_price}... more expensive than before :(')

        elif currently_in_stock and not previously_in_stock:

            # if no pricing is available, we'll assume the price is low enough
            if current_price is None:
                self.send_alert(s, result, 'now in stock!')

            # is the current price low enough?
            elif self.max_price is None or current_price <= self.max_price:
                self.send_alert(s, result, f'now in stock at {current_price}!')

            else:
                s.logger.info(f'now in stock at {current_price}... too expensive')

        elif not currently_in_stock and result.has_phrase('are you a human'):

            s.logger.error('got "are you a human" prompt')
            self.alerter('Something went wrong',
                         f'You need to answer this CAPTCHA and restart this script: {result.url}')
            sys.exit(1)

        else:
            s.logger.info('not in stock')

    def send_alert(self, s, result, reason):
        s.logger.info(reason)
        self.alerter(subject=result.alert_subject, content=result.alert_content)


def hunt(args, config, scrapers):
    engine = Engine(args, config, scrapers)
    engine.run()
