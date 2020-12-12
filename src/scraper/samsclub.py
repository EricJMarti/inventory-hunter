from scraper.common import ScrapeResult, Scraper, ScraperFactory


class SamsclubScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get listed price
        tag = self.soup.body.select_one('div.sc-pc-single-price > span > span > span.Price-characteristic')
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'
        else:
            self.logger.warning(f'missing price: {self.url}')

        # get name of product
        tag = self.soup.body.select_one('div.sc-pc-title-full-desktop > h1')
        if tag:
            alert_content += tag.text.strip() + '\n'
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'
        else:
            tag = self.soup.body.select_one('div.sc-pc-title-medium.sc-pc-large-desktop-oos-card-description-title > h3')
            if tag:
                alert_content += tag.text.strip() + '\n'
            else:
                self.logger.warning(f'missing title: {self.url}')



@ScraperFactory.register
class SamsclubScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'samsclub'

    @staticmethod
    def get_driver_type():
        return 'selenium'

    @staticmethod
    def get_result_type():
        return SamsclubScrapeResult
