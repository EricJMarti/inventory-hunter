import scraper.amazon
import scraper.bestbuy
import scraper.bhphotovideo
import scraper.microcenter
import scraper.newegg

from scraper.common import ScraperFactory


def init_scrapers(config, drivers):
    return [ScraperFactory.create(drivers, url) for url in config.urls]
