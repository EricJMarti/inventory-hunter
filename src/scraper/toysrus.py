from scraper.common import ScrapeResult, Scraper, ScraperFactory


class ToysRUsScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('.b-product_details-name')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('.b-price-value.js-sales-price-value')
        price_str = self.set_price(tag.getText())
        if price_str:
            alert_subject = f'In Stock for {price_str}'
        else:
            self.logger.warning(f'missing price: {self.url}')

        # check for add to cart button
        tag = self.soup.body.select_one('li.b-product_status')
        if tag and 'in stock' in str(tag).lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class ToysRUsScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'toysrus'

    @staticmethod
    def get_driver_type():
        return 'requests'

    @staticmethod
    def get_result_type():
        return ToysRUsScrapeResult
