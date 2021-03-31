from scraper.common import ScrapeResult, Scraper, ScraperFactory
import re


class EbuyerScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('#main-content > div > div.product-left-col > div.product-hero.js-product-hero > h1')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('#main-content > div > div.product-right-col > div.purchase-info > div.purchase-info__price > div.inc-vat > p')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = self.soup.body.select_one('#main-content > div > div.product-right-col > div.purchase-info > div.purchase-info__cta > form > input.button.button--add-to-basket.js-add-to-basket.js-add-to-basket-main.js-show-loader')
        if tag:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class EbuyerScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'ebuyer'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return EbuyerScrapeResult
