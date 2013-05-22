# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class GScholarCitationItem(Item):
    title = Field()
    authors = Field()
    pubDate = Field()
    pubUrl = Field()
    publisher = Field()
    abstract = Field()
    citedBy = Field()
    authorId = Field()
   
    
    
