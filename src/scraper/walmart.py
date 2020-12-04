from scraper.common import ScrapeResult, Scraper, ScraperFactory


class WalmartScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('h1.prod-ProductTitle.prod-productTitle-buyBox.font-bold')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('section.prod-PriceSection div.prod-PriceHero span.price-group')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'
        else:
            self.logger.warning(f'missing price: {self.url}')

        # check for add to cart button
        tag = self.soup.body.select_one('section.prod-ProductCTA.primaryProductCTA-marker button')
        if tag and 'add to cart' in str(tag).lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class WalmartScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'walmart'

    @staticmethod
    def get_driver_type():
        return 'requests'

    @staticmethod
    def get_result_type():
        return WalmartScrapeResult
