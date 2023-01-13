from scraper.common import ScrapeResult, Scraper, ScraperFactory


class JlcpcbScrapeResult(ScrapeResult):
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
            #tag = details.select_one('div.smt-count-component ')
            #self.logger.warning(tag)
            tag = details.select_one('div.smt-count-component td.el-table_1_column_2 span')
            if tag:
                extracted_price_str = str(tag.get_text()).split()[-1]
                price_str = self.set_price(extracted_price_str)
                if price_str:
                    alert_subject = f'In Stock for {price_str}'
                else:
                    self.logger.warning(f'failed to extract price: {self.url}')
            else:
                self.logger.warning(f'missing price element: {self.url}')

            # check for in-store inventory
            tag = details.select_one('div.smt-count-component:first-child > div:first-child > div:first-child > div:first-child ~ button + p')
            if tag and 'available order qty' in str(tag.get_text()).lower():
                qty = int(str(tag.get_text()).split()[-1])
                if qty > 0:
                    alert_content += f'Available quantity: {qty}'
                    self.alert_subject = alert_subject
                    self.alert_content = f'{alert_content.strip()}\n{self.url}'
            else:
                self.logger.warning(f'Missing quantity element: {self.url}')

        else:
            self.logger.warning(f'missing layout div: {self.url}')


@ScraperFactory.register
class JlcpcbScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'jlcpcb'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return JlcpcbScrapeResult
