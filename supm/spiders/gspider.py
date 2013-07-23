from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

import MySQLdb
import re
import json
from datetime import datetime

#from supm.items import GScholarItem
from supm.items import GScholarCitationItem, ScopusCitationItem

def getAuthorsAndUrls():
    #MUST CHANGE THIS to the correct parameters
    mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
    mydb.autocommit(True)
    mydb.set_character_set('utf8')
    cursor = mydb.cursor()
    cursor.execute("SELECT id, gscholar_id, scopus_id FROM authors")
    rows = cursor.fetchall()
    cursor.close()
    return rows

class Test(BaseSpider):
    name = "gspider"
    lcount = 0
    authorID = 0
    allowed_domains = ["scholar.google.com"]
    
    def start_requests(self):
        for row in getAuthorsAndUrls():
            
            #Google Scholar Link
            if row[1]:
                self.authorID = row[0]
                link = 'http://scholar.google.com/citations?user='+row[1]+'&pagesize=20'
                yield Request(url=link,callback=self.parseGScholar,meta={'authorId': str(row[0])})
                
            #Scopus Link
            if row[2]:
                self.authorID = row[0]
                link = 'http://searchapi.scopus.com/documentSearch.url?apiKey=e216a9f5c60ecf6f105ba5225a09f99b&search=AU-ID('+str(row[2])+')&numResults=200'
                yield Request(url=link,callback=self.parseScopus,meta={'authorId': str(row[0])})
   
    #Function to parse ans scrap google scholar publications
    def parseGScholar(self, response):
        
        hxs = HtmlXPathSelector(response)
        
        #Extracting links and publication year
        for tableItem in hxs.select('//tr[@class="cit-table item"]'):
            link = ''.join(tableItem.select('td[@id="col-title"]/a[@class="cit-dark-large-link"]/@href').extract())
            link = "http://scholar.google.com"+link
            year = tableItem.select('td[@id="col-year"]/text()').extract()
            yield Request(url=link, callback=self.processGSLink,meta={'authorId': response.meta['authorId'],'pubDate': year})
        
        
        #handling pagination
        for nextPage in hxs.select('//td[@style="text-align:right;"]/a[@class="cit-dark-link"]/@href').extract():
            nextPage = "http://scholar.google.com" + nextPage
            yield Request(url=nextPage, callback=self.parseGScholar,meta={'authorId': response.meta['authorId']})
        
    #Function to extract data from publications of Google Shcolar pages.
    def processGSLink(self,response):
        
        item = GScholarCitationItem()
        
        self.log('url: %s' % response.url)
        self.lcount += 1
        self.log('Citation number %d ' % self.lcount)
        
        hxs = HtmlXPathSelector(response)
        
        #2 Types of title one inside <a></a> and another without it.
        title = hxs.select('//div[@id="title"]/a/text()').extract()
        if len(title) == 0:
            title = hxs.select('//div[@id="title"]/text()').extract()
        
        #item['title'] = ''.join(title).encode('iso-8859-1','ignore')
        item['title'] = ''.join(title)
        item['authors'] = ''.join(hxs.select('//div[@id="main_sec"]/div[@class="cit-dl"]/div[@class="g-section"][1]/div[@class="cit-dd"]/text()').extract())
        item['publisher'] = ''.join(hxs.select('//div[@id="publisher_sec"]/div[@class="cit-dd"]/text()').extract())
        item['abstract'] = ''.join(hxs.select('//div[@id="description_sec"]/div[@class="cit-dd"]/text()').extract())
        item['citedBy'] = ''.join(hxs.select('//div[@id="scholar_sec"]/div/a[@class="cit-dark-link"]/text()').re(r'[0-9]+'))
        item['pubUrl'] = str(response.url)
        item['authorId'] = response.meta['authorId']
        item['pubDate'] = ''.join(response.meta['pubDate'])
        item['docUID'] = re.match('(.*)(=)(.+)',item['pubUrl']).group(3)
        item['source'] = 'Google Scholar'
        
        #Strip the last part or the URL to get the document URI
        if item['citedBy'] == "":
                item['citedBy'] = "0"
        
        return item
    
    #Extracting data from scopus pages 
    def parseScopus(self,response):
        
        item = ScopusCitationItem()
        
        #Since the data obtained from scopus links is in
        #JSON format we extract the valid JSON results
        #and parse them into ScopusCitationItems
        data = re.search('null\((.+)\)',response.body).group(1) 

        scopusData = json.loads(data)
        
        #print 'Authors results: ' + str(len(scopusData['OK']['results']))
        
        #Extracting publication items
        for pub in scopusData['OK']['results']:
            
            item['authorId'] = response.meta['authorId']
            item['title'] = pub['title']
            item['pubType'] = pub['doctype'] #In the database we refer to this item as publication type (journal, Book,etc.)
            item['citedBy'] = pub['citedbycount']
            item['docUID'] = pub['eid']
            item['pubUrl'] = pub['inwardurl']
            item['pubDate'] =  str(datetime.strptime(pub['pubdate'],'%Y-%m-%d').year)
            item['source'] = 'Scopus'
            yield item






