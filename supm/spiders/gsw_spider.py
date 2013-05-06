from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector
import sys

#from supm.items import GScholarItem
from supm.items import GScholarCitationItem

class GScholarSpider(CrawlSpider):
    name = "gsw"

    def __init__(self, user=None):
        super(GScholarSpider,self).__init__(user)
        if user == None:
            sys.exit("\nNo user ID has been specified\n")
        else:
            self.allowed_domains = ["scholar.google.com"]
            self.start_urls = ["http://scholar.google.com/citations?user=%s&pagesize=100" % user] #zwSj1n8AAAAJ user de concha

    rules = (Rule(SgmlLinkExtractor(allow='/citations?hl=en&user=.+&pagesize=100&view_op=list_works&cstart=[0-9]+'),follow=True),
                  Rule(SgmlLinkExtractor(allow='/citations\?view_op=view_citation.?', ), callback='parse_item')
             )
    
    #http://scholar.google.es/citations?view_op=view_citation&hl=en&user=9zrv6BMAAAAJ&pagesize=100&citation_for_view=9zrv6BMAAAAJ:u5HHmVD_uO8C

    """def parse_start_url(self, response):
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
        return items"""

    def parse_item(self, response):
        self.log('Hi, this is an citation! %s' % response.url)

        hxs = HtmlXPathSelector(response)
        
        item = GScholarCitationItem()
        
        item['title'] = ''.join(hxs.select('//div[@id="title"]/a/text()').extract()).encode('iso-8859-1','ignore')
        item['authors'] = ''.join(hxs.select('//div[@class="g-section"][1]/div[@class="cit-dd"]/text()').extract()).encode('iso-8859-1','ignore')
        item['pubDate'] = ''.join(hxs.select('//div[@id="pubdate_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['publisher'] = ''.join(hxs.select('//div[@id="publisher_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['abstract'] = ''.join(hxs.select('//div[@id="description_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['citedBy'] = ''.join(hxs.select('//div[@id="scholar_sec"]/div/a[@class="cit-dark-link"]/text()').re(r'[0-9]+')).encode('utf-8')

        
        self.log('AUTHORS --  %s ' % item['authors'])
        
        return item
        
