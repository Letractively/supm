from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

import MySQLdb

#from supm.items import GScholarItem
from supm.items import GScholarCitationItem

def getAuthorsAndUrls():
    #MUST CHANGE THIS to the correct parameters
    mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
    mydb.autocommit(True)
    mydb.set_character_set('utf8')
    cursor = mydb.cursor()
    cursor.execute("SELECT id, gscholar_id FROM authors")
    rows = cursor.fetchall()
    cursor.close()
    
    return rows

class Test(BaseSpider):
    name = "gspider"
    lcount = 0
    authorID = 0
    allowed_domains = ["scholar.google.com"]
    
    #f = open("start_urls.txt")
    #authorIds = [ row[0] for row in authorsAndStartUrl]
    #start_urls = [ 'http://scholar.google.com/citations?user='+row[1]+'&pagesize=20' for row in authorsAndStartUrl if row[1]]
    
    def start_requests(self):
        for row in getAuthorsAndUrls():
            if row[1]:
                self.authorID = row[0]
                link = 'http://scholar.google.com/citations?user='+row[1]+'&pagesize=20'
                yield Request(url=link,callback=self.parse,meta={'authorId': str(row[0])})
   
    #start_urls = [url.strip() for url in f.readlines()]
    #f.close()
    #start_urls = ["http://scholar.google.com/citations?user=zwSj1n8AAAAJ&pagesize=20"] #zwSj1n8AAAAJ user de concha
    
    def parse(self, response):
        
        hxs = HtmlXPathSelector(response)
        
        #Extracting links and publication year
        for tableItem in hxs.select('//tr[@class="cit-table item"]'):
        #link = "http://scholar.google.com"+link
            link = ''.join(tableItem.select('td[@id="col-title"]/a[@class="cit-dark-large-link"]/@href').extract())
            #print link
            link = "http://scholar.google.com"+link
            year = tableItem.select('td[@id="col-year"]/text()').extract()
            yield Request(url=link, callback=self.process_link,meta={'authorId': response.meta['authorId'],'pubDate': year})
        
        
        #extracting links from current page
        #for link in hxs.select('//td[@id="col-title"]/a[@class="cit-dark-large-link"]/@href').extract():
        #    link = "http://scholar.google.com"+link
        #    yield Request(url=link, callback=self.process_link,meta={'authorId': response.meta['authorId']})
        
        #handling pagination
        for nextPage in hxs.select('//td[@style="text-align:right;"]/a[@class="cit-dark-link"]/@href').extract():
            nextPage = "http://scholar.google.com" + nextPage
            yield Request(url=nextPage, callback=self.parse,meta={'authorId': response.meta['authorId']})
        
    def process_link(self,response):
        
        item = GScholarCitationItem()
        
        self.log('url: %s' % response.url)
        self.lcount += 1
        self.log('Citation number %d ' % self.lcount)
        
        hxs = HtmlXPathSelector(response)
        
        item['title'] = ''.join(hxs.select('//div[@id="title"]/a/text()').extract()).encode('iso-8859-1','ignore')
        item['authors'] = ''.join(hxs.select('//div[@id="main_sec"]/div[@class="cit-dl"]/div[@class="g-section"][1]/div[@class="cit-dd"]/text()').extract()).encode('iso-8859-1','ignore')
        #item['pubDate'] = ''.join(hxs.select('//div[@id="pubdate_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['publisher'] = ''.join(hxs.select('//div[@id="publisher_sec"]/div[@class="cit-dd"]/text()').extract()).encode('utf-8')
        item['abstract'] = ''.join(hxs.select('//div[@id="description_sec"]/div[@class="cit-dd"]/text()').extract()).encode('iso-8859-1','ignore')
        item['citedBy'] = ''.join(hxs.select('//div[@id="scholar_sec"]/div/a[@class="cit-dark-link"]/text()').re(r'[0-9]+')).encode('utf-8')
        item['pubUrl'] = str(response.url)
        item['authorId'] = response.meta['authorId']
        item['pubDate'] = ''.join(response.meta['pubDate']).encode('utf-8')
        
        return item