from scraper.common import ScrapeResult, Scraper, ScraperFactory


class DigikeyDeScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        details = self.soup.body.find('div', id='__layout')
        if details:

            # get name of product
            tag = details.select_one('h1')
            if tag:
                alert_content += tag.text.strip() + '\n'
            else:
                self.logger.warning(f'missing title: {self.url}')

            # get listed price
            tag = details.select_one('div[data-testid="vat-tax"] tbody tr + tr > td')
            extracted_price_str = str(tag)
            price_str = self.set_price(extracted_price_str)
            if price_str:
                alert_subject = f'In Stock for {price_str}'
            else:
                self.logger.warning(f'missing price: {self.url}')

            # check for in-store inventory
            tag = details.select_one('div[data-testid="price-and-procure-title"] span')
            if tag and 'available order qty' in str(tag).lower():
                qty = int(str(tag).split()[0])
                if qty > 0:
                    alert_content += f'Available quantity: {qty}'
                    self.alert_subject = alert_subject
                    self.alert_content = f'{alert_content.strip()}\n{self.url}'
            else:
                self.logger.warning(f'Missing quantity information: {self.url}')

        else:
            self.logger.warning(f'missing layout div: {self.url}')


@ScraperFactory.register
class DigikeyDeScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'digikey.de'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return DigikeyDeScrapeResult
