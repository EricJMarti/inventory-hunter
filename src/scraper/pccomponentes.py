from scraper.common import ScrapeResult, Scraper, ScraperFactory

import logging


class PCComponentesResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('h1.h4 > strong')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag1 = self.soup.body.select_one('span.baseprice')
        tag2 = self.soup.body.select_one('span.cents')
        print(f'tag1: {tag1}')
        print(f'tag2: {tag2}')
        logging.warning(f'tag1: {tag1}')
        logging.warning(f'tag2: {tag2}')
        price_str = self.set_price(tag1 +""+ tag2)
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = self.soup.body.select_one('button.btn.js-article-buy.btn-primary.btn-lg.buy.GTM-addToCart.buy-button > strong')
        if tag:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class PCComponentesScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'pccomponentes'

    @staticmethod
    def get_driver_type():
        return 'selenium'

    @staticmethod
    def get_result_type():
        return PCComponentesResult
