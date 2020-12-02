import scraper.amazon
import scraper.bestbuy
import scraper.bhphotovideo
import scraper.microcenter
import scraper.newegg

from scraper.common import ScraperFactory


def init_scrapers(driver, urls: list):
    return [ScraperFactory.create(driver, url) for url in urls]
