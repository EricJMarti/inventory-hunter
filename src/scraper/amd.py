from scraper.common import ScrapeResult, Scraper, ScraperFactory


class AmdScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('div.product-page-description.col-flex-lg-5.col-flex-sm-12 > h2')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('div.product-page-description.col-flex-lg-5.col-flex-sm-12 > h4').get_text()
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = self.soup.body.select_one('div.product-page-description.col-flex-lg-5.col-flex-sm-12 > button')
        if tag:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class AmdScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'amd'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return AmdScrapeResult
