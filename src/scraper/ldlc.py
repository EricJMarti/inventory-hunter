from scraper.common import ScrapeResult, Scraper, ScraperFactory


class LdlcScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('#activeOffer > div.title > h1')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('#activeOffer > div.product-info > div.wrap-aside > aside > div.price > div')
        price_str = self.set_price(tag).replace('€', ',') + '€'
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = self.soup.body.select_one('#product-page-stock > div.website > div.content > div > span > em')
        if tag:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class LdlcScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'ldlc'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return LdlcScrapeResult
