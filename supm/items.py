# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class GScholarItem(Item):
    authors = Field()
    title = Field()
    url = Field()
    year = Field()
    citedBy = Field()
    
