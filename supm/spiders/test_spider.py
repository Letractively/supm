#from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import BaseSpider
#from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.http import Request

from scrapy.selector import HtmlXPathSelector
#import sys


#from supm.items import GScholarItem
from supm.items import GScholarCitationItem

class Test(BaseSpider):
    name = "test"
    lcount = 0
    
    allowed_domains = ["scholar.google.com"]
    
    f = open("start_urls.txt")
    start_urls = [url.strip() for url in f.readlines()]
    f.close()
    #start_urls = ["http://scholar.google.com/citations?user=zwSj1n8AAAAJ&pagesize=20"] #zwSj1n8AAAAJ user de concha
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        #extracting links from current page
        for link in hxs.select('//td[@id="col-title"]/a[@class="cit-dark-large-link"]/@href').extract():
            link = "http://scholar.google.com"+link
            yield Request(url=link, callback=self.process_link)
        
        #handling pagination
        for nextPage in hxs.select('//td[@style="text-align:right;"]/a[@class="cit-dark-link"]/@href').extract():
            nextPage = "http://scholar.google.com" + nextPage
            yield Request(url=nextPage, callback=self.parse)
        
            

    def process_link(self,response):
        
        item = GScholarCitationItem()
        
        self.log('url: %s' % response.url)
        self.lcount += 1
        self.log('Citation number %d ' % self.lcount)
        
        hxs = HtmlXPathSelector(response)
        
        item['title'] = ''.join(hxs.select('//div[@id="title"]/a/text()').extract()).encode('iso-8859-1','ignore')
        item['authors'] = ''.join(hxs.select('//div[@class="g-section"][1]/div[@class="cit-dd"]/text()').extract()).encode('iso-8859-1','ignore')
        item['pubDate'] = ''.join(hxs.select('//div[@id="pubdate_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['publisher'] = ''.join(hxs.select('//div[@id="publisher_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['abstract'] = ''.join(hxs.select('//div[@id="description_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['citedBy'] = ''.join(hxs.select('//div[@id="scholar_sec"]/div/a[@class="cit-dark-link"]/text()').re(r'[0-9]+')).encode('utf-8')
        
        
        return item