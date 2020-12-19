from scraper.common import ScrapeResult, Scraper, ScraperFactory


class PlayStationScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        product = self.soup.body.find('div', class_='productHero-info')
        if not product:
            tag = self.soup.body.find('div', id='challenge-container')
            if tag:
                self.logger.warning('access denied, got a CAPTCHA')
            else:
                self.logger.warning(f'missing product info div: {self.url}')
            return

        # get name of product
        tag = product.find('h1')
        if not tag:
            tag = product.find('h2')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = product.find('div', class_='price-text')
        if tag:
            price_symbol = tag.find('sup', class_='js-actual-price-symbol')
            price_whole = tag.find('span', class_='js-actual-price-whole')
            price_fraction = tag.find('sup', class_='js-actual-price-fraction')
            if price_symbol and price_whole and price_fraction:
                price_str = self.set_price(f'{price_symbol.text.strip()}{price_whole.text.strip()}.{price_fraction.text.strip()}')
                if price_str:
                    alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = product.select_one('div.button-placeholder > button.add-to-cart')
        if tag and 'add' in tag.text.lower() and 'hide' not in tag.attrs['class']:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class PlayStationScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'playstation'

    @staticmethod
    def get_driver_type():
        return 'selenium'

    @staticmethod
    def get_result_type():
        return PlayStationScrapeResult
