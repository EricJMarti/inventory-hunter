from scraper.common import ScrapeResult, Scraper, ScraperFactory


class AdoramaScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # detect product or captcha
        product = self.soup.body.find('div', class_='product-info-container')
        if not product:
            tag = self.soup.body.find('div', id='px-captcha')
            if tag:
                self.captcha = True
            else:
                self.logger.warning(f'missing product info div: {self.url}')
            return

        # get name of product
        tag = product.find('h1')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = product.find('strong', class_='your-price')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = product.select_one('div.buy-section button.add-to-cart')
        if tag and 'add to cart' in tag.text.lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class AdoramaScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'adorama'

    @staticmethod
    def get_driver_type():
        return 'selenium'

    @staticmethod
    def get_result_type():
        return AdoramaScrapeResult
