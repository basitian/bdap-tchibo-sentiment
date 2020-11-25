# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html



from scrapy.exceptions import DropItem

import psycopg2

class SavePipeline:

    def __init__(self, postgre_host, postgre_database, postgre_user, postgre_password):
        self.host = postgre_host
        self.database = postgre_database
        self.user = postgre_user
        self.password = postgre_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            postgre_host = crawler.settings.get('DB_HOST'),
            postgre_database = crawler.settings.get('DB_NAME', 'items'),
            postgre_user = crawler.settings.get('DB_USER'),
            postgre_password = crawler.settings.get('DB_PASSWORD'),
        )

    def open_spider(self, spider):
        self.connection = None
        self.cursor = None
        try:
            print('Connecting to the PostgreSQL database...')
            self.connection = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
            self.cursor = self.connection.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def close_spider(self, spider):
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()
            print('Database connection closed...')

    def process_item(self, item, spider):
        try:
            if self.cursor is not None:
                self.cursor.execute( 'SELECT * FROM "Reviews" WHERE "SourceReviewId"=\'{}\' AND "Source"=\'otto.de\''.format(item['SourceReviewId']) )
                review = self.cursor.fetchone()

                if review is None:
                    self.cursor.execute('INSERT INTO "Reviews" ("ProductName", "Rating", "CreatedAt", "ReviewTitle", "Source", "ReviewText", "SourceReviewId") VALUES (\'{}\', {}, \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'.format(
                                        item['ProductName'], 
                                        item['Rating'],
                                        item['CreatedAt'],
                                        item['ReviewTitle'],
                                        item['Source'],
                                        item['ReviewText'],
                                        item['SourceReviewId']))
                    self.connection.commit()
                    return item
                else: 
                    raise DropItem(f"Review {item['SourceReviewId']} from otto.de already exists")
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return item
