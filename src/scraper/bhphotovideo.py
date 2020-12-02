import logging
import re

from scraper.common import ScrapeResult, Scraper, ScraperFactory


class BHPhotoVideoScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.find('div', class_=re.compile('title_.*'))
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            logging.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.find('div', class_=re.compile('pricesContainer_.*'))
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'
        else:
            logging.warning(f'missing price: {self.url}')

        # check for add to cart button
        tag = self.soup.body.find('button', class_=re.compile('toCartBtn.*'))
        if tag and 'add to cart' in tag.text.lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class BHPhotoVideoScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'bhphotovideo'

    @staticmethod
    def get_driver_type():
        return 'requests'

    @staticmethod
    def get_result_type():
        return BHPhotoVideoScrapeResult

    @staticmethod
    def generate_short_name(url):
        parts = [i for i in url.path.split('/') if i]
        if parts:
            return parts[-1].replace('.html', '')
