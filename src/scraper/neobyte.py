from scraper.common import ScrapeResult, Scraper, ScraperFactory


class NeobyteResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('h1.h1.page-title > span')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('span.current-price > span.product-price')
        price_str = self.set_price(tag["content"])
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = self.soup.body.select_one('span#product-availability > i.fa.fa-check.rtl-no-flip')
        if tag:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class NeobyteScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'neobyte'

    @staticmethod
    def get_driver_type():
        return 'requests'

    @staticmethod
    def get_result_type():
        return NeobyteResult
