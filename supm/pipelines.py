# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import sys
import MySQLdb

from supm.items import GScholarItem
from supm.items import GScholarCitationItem

class SupmPipeline(object):
    def process_item(self, item, spider):
        return item

class GScholarPipeline(object):

    def __init__(self):
        #self.file = open('scraped.xml','ab')
        #self.file.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n<author>\n')
        self.db = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
        self.db.autocommit(True)
        self.cursor = self.db.cursor()
        
        
    def process_item(self,item,spider):

        if isinstance(item,GScholarItem):
            #process GScholarItem
            """self.file.write("<publication>\n")
            self.file.write("<title>%s</title>\n" % ''.join(item['title']).encode('utf-8').strip())
            self.file.write("<authors>%s</authors>\n" % ''.join(item['authors']).encode('utf-8').strip())
            #self.file.write("<url>%s</url>\n" % ''.join(item['url']).encode('utf-8').strip())
            self.file.write("<year>%s</year>\n" % ''.join(item['year']).encode('utf-8').strip())
            self.file.write("<citedBy>%s</citedBy>\n" % ''.join(item['citedBy']).encode('utf-8').strip())
            self.file.write("</publication>\n")"""
                        
        if isinstance(item,GScholarCitationItem):
            #process CitationItem
            """self.file.write("<citation>\n")
            self.file.write("<authors>%s</authors>\n" % ''.join(item['authors']).encode('utf-8').strip())
            self.file.write("<title>%s</title>\n" % ''.join(item['title']).encode('utf-8').strip())
            self.file.write("<pubDate>%s</pubDate>\n" % ''.join(item['pubDate']).encode('utf-8').strip())
            self.file.write("<publisher>%s</publisher>\n" % ''.join(item['publisher']).encode('utf-8').strip())
            self.file.write("<abstract>%s</abstract>\n" % ''.join(item['abstract']).encode('utf-8').strip())
            self.file.write("</citation>\n")"""


            authors = item['authors']
            title = item['title']
            publisher = item['publisher']
            times_cited = item['citedBy']
            abstract = item['abstract']
            year = item['pubDate']
            
            
            self.cursor.execute("INSERT INTO publications (title,authors,publisher,times_cited,year) VALUES ('%s', '%s', '%s', '%s', '%s')"
                                % (title,authors,publisher,times_cited,year))
                                                    
        return item
    
    def close_pider(spider):
        self.file.write('\n</author>')
        self.file.close()

        


