from scraper.common import ScrapeResult, Scraper, ScraperFactory


class AmazonScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('h1#title > span#productTitle')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('div.a-section > span#price_inside_buybox')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to basket button
        tag = self.soup.body.select_one('span.a-button-inner > span#submit\\.add-to-basket-announce')
        if tag and 'add to basket' in tag.text.lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class AmazonScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'amazon'

    @staticmethod
    def get_driver_type():
        return 'selenium'

    @staticmethod
    def get_result_type():
        return AmazonScrapeResult
