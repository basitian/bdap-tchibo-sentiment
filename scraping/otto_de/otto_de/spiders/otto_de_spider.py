import scrapy
import json

from otto_de.items import Review

class OttoReviewsSpider(scrapy.Spider):
    name = "otto_reviews"

    def start_requests(self):
        yield scrapy.Request(f'https://www.otto.de/product-customerreview/reviews/presentation/product/{self.productId}')

    def parse(self, response):
        result = json.loads(response.body)
        for review in result['items']:
            data = review['data']
            review = Review()
            review['ProductName'] = data['articleName']
            review['Rating'] = data['rating']
            review['CreatedAt'] = data['creationDate']
            review['ReviewTitle'] = data['title']
            review['ReviewText'] = data['text']
            review['Source'] = 'otto.de'
            review['SourceReviewId'] = data['id']
            yield review