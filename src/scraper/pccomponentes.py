from scraper.common import ScrapeResult, Scraper, ScraperFactory


class PccomponentesScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('#contenedor-principal > div:nth-child(2) > div > div:nth-child(3) > div > div > div.articulo > h1 > strong')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('#precio-main')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = self.soup.body.select_one('#btnsWishAddBuy > button.btn.js-article-buy.btn-primary.btn-lg.buy.GTM-addToCart.buy-button')
        if tag:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class PccomponentesScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'pccomponentes'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return PccomponentesScrapeResult
