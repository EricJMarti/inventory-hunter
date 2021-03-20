import json


from scraper.common import ScrapeResult, Scraper, ScraperFactory


class GameStopScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        details = self.soup.body.find('div', class_='product-details-container')
        if details:

            # get name of product
            tag = details.find('h1', class_='product-name')
            if tag:
                alert_content += tag.text.strip() + '\n'
            else:
                self.logger.warning(f'missing title: {self.url}')

            primary_details = details.find('div', id='primary-details')
            if primary_details:

                # get listed price
                tag = primary_details.select_one('span.selling-price-redesign > span.actual-price')
                price_str = self.set_price(tag)
                if price_str:
                    alert_subject = f'In Stock for {price_str}'
                else:
                    self.logger.warning(f'missing price: {self.url}')

                # check for add to cart button
                tag = primary_details.select_one('div.add-to-cart-buttons > div.atc-btns-wrapper > div.atc-btn-wrapper > button.add-to-cart')
                if json.loads(tag['data-gtmdata'])['productInfo']['availability'] == 'Available':
                    self.alert_subject = alert_subject
                    self.alert_content = f'{alert_content.strip()}\n{self.url}'

            else:
                self.logger.warning(f'missing primary details container: {self.url}')
        else:
            self.logger.warning(f'missing product details container: {self.url}')


@ScraperFactory.register
class GameStopScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'gamestop'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return GameStopScrapeResult
