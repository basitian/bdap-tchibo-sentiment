# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Review(Item):
    # define the fields for your item here like:
    ProductName = Field()
    Rating = Field()
    CreatedAt = Field()
    ReviewTitle = Field()
    ReviewText = Field()
    Source = Field()
    SourceReviewId = Field()