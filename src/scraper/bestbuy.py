from scraper.common import ScrapeResult, Scraper, ScraperFactory


class BestBuyScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.find('div', class_='sku-title')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('div.priceView-customer-price > span')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'
        else:
            self.logger.warning(f'missing price: {self.url}')

        # check for add to cart button
        tag = self.soup.body.find('div', class_='fulfillment-add-to-cart-button')
        if tag and 'add to cart' in tag.text.lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class BestBuyScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'bestbuy'

    @staticmethod
    def get_driver_type():
        return 'requests'

    @staticmethod
    def get_result_type():
        return BestBuyScrapeResult
