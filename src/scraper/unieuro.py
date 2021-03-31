from scraper.common import ScrapeResult, Scraper, ScraperFactory


class UnieuroScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.select_one('#features > div.details-table > section.container-center-cell > h1')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            self.logger.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.select_one('#features > div.details-table > section.container-right-cell.anonymous > div.prices-content > div')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'

        # check for add to cart button
        tag = self.soup.body.select_one('#features > div.details-table > section.container-right-cell.anonymous > article.price-container > div > div > div.buttons-container > div')
        if tag:
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


@ScraperFactory.register
class UnieuroScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'unieuro'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return UnieuroScrapeResult
