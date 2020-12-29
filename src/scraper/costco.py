from scraper.common import ScrapeResult, Scraper, ScraperFactory


class CostcoScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # detect product or captcha
        product = self.soup.body.find('div', class_='top-content')
        if not product:
            self.logger.warning(f'missing product div: {self.url}')
            return

        # get name of product
        tag = product.find('h1')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = product.find('div', id='pull-right-price')
        if tag:
            price_currency = tag.find('span', class_='currency')
            price_value = tag.find('span', class_='value')
            if price_currency and price_value:
                price_str = self.set_price(f'{price_currency.text.strip()}{price_value.text.strip()}')
                if price_str:
                    alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = product.select_one('div#add-to-cart > input#add-to-cart-btn.primary-button-v2')
        if tag and 'add to cart' in tag.attrs['value'].lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class CostcoScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'costco'

    @staticmethod
    def get_driver_type():
        return 'selenium'

    @staticmethod
    def get_result_type():
        return CostcoScrapeResult
