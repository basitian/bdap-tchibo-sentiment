from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from otto_de.spiders.otto_de_spider import OttoReviewsSpider

process = CrawlerProcess(get_project_settings())
process.crawl(OttoReviewsSpider, productId=723800867)
process.start()