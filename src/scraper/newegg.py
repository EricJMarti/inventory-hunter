import logging

from scraper.common import ScrapeResult, Scraper, ScraperFactory


class NeweggScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.find('h1', class_='product-title')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            logging.warning(f'missing title: {self.url}')

        buy_box = self.soup.body.find('div', class_='product-buy-box')
        if buy_box:

            # get listed price
            tag = buy_box.find('li', class_='price-current')
            price_str = self.set_price(tag)
            if price_str:
                alert_subject = f'In Stock for {price_str}'
            else:
                logging.warning(f'missing price: {self.url}')

            # check for add to cart button
            tag = buy_box.find('div', class_='product-buy')
            if tag:
                if 'add to cart' in tag.text.lower():
                    self.alert_subject = alert_subject
                    self.alert_content = f'{alert_content.strip()}\n{self.url}'
            else:
                logging.warning(f'missing add to cart button: {self.url}')

        else:
            logging.warning(f'missing buy box: {self.url}')


@ScraperFactory.register
class NeweggScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'newegg'

    @staticmethod
    def get_driver_type():
        return 'requests'

    @staticmethod
    def get_result_type():
        return NeweggScrapeResult

    @staticmethod
    def generate_short_name(url):
        parts = [i for i in url.path.split('/') if i]
        if parts:
            return parts[0]
