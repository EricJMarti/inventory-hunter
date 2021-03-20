from scraper.common import ScrapeResult, Scraper, ScraperFactory


class NeweggScrapeResult(ScrapeResult):
    def parse(self):
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        is_combo = False
        tag = self.soup.body.find('h1', class_='product-title')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            # check if this is a combo
            tag = self.soup.body.select_one('div.grpDesc > div.wrapper > h1')
            if tag:
                alert_content += tag.text.strip() + '\n'
                is_combo = True
            else:
                self.logger.warning(f'missing title: {self.url}')

        if is_combo:
            buy_box = self.soup.body.find('div', class_='grpPricing')
            if buy_box:

                # get listed price
                tag = buy_box.select_one('div#singleFinalPrice.current')
                price_str = self.set_price(tag.text.replace('Now:', ''))
                if price_str:
                    alert_subject = f'In Stock for {price_str}'
                else:
                    self.logger.warning(f'missing combo price: {self.url}')

                # check for add to cart button
                tag = buy_box.select_one('div.grpAction > a.atnPrimary')
                if tag:
                    if 'add to cart' in tag.text.lower():
                        self.alert_subject = alert_subject
                        self.alert_content = f'{alert_content.strip()}\n{self.url}'
                else:
                    self.logger.warning(f'missing combo add to cart button: {self.url}')

            else:
                self.logger.warning(f'missing combo buy box: {self.url}')

        else:
            buy_box = self.soup.body.find('div', class_='product-buy-box')
            if buy_box:

                # get listed price
                tag = buy_box.find('li', class_='price-current')
                price_str = self.set_price(tag)
                if price_str:
                    alert_subject = f'In Stock for {price_str}'
                else:
                    self.logger.warning(f'missing price: {self.url}')

                # check for add to cart button
                tag = buy_box.find('div', class_='product-buy')
                if tag:
                    if 'add to cart' in tag.text.lower():
                        self.alert_subject = alert_subject
                        self.alert_content = f'{alert_content.strip()}\n{self.url}'
                else:
                    self.logger.warning(f'missing add to cart button: {self.url}')

            else:
                self.logger.warning(f'missing buy box: {self.url}')


@ScraperFactory.register
class NeweggScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'newegg'

    @staticmethod
    def get_driver_type():
        return 'lean_and_mean'

    @staticmethod
    def get_result_type():
        return NeweggScrapeResult
