from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from supm.items import GScholarItem

class GScholarSpider(BaseSpider):
    name = "gscholar"
    allowed_domains = ["scholar.google.es"]
    start_urls = [
        "http://scholar.google.es/citations?user=zwSj1n8AAAAJ",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        publications = hxs.select('//tr[@class="cit-table item"]')
        items = []

        for publication in publications:
             item = GScholarItem()
             item['title'] = publication.select('td/a[@class="cit-dark-large-link"]/text()').extract()
             item['url'] = publication.select('td/a[@class="cit-dark-large-link"]/@href').extract()
             item['year'] = publication.select('td[@id="col-year"]/text()').extract()
             item['authors'] = publication.select('td/span[1][@class="cit-gray"]/text()').extract()
             item['citedBy'] = publication.select('td[@id="col-citedby"]/a[@class="cit-dark-link"]/text()').extract()
             items.append(item)
        return items
