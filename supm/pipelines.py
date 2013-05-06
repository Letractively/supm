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
        self.db = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
        self.db.autocommit(True)
        self.cursor = self.db.cursor()
        
        
    def process_item(self,item,spider):

#        if isinstance(item,GScholarItem):
            #process GScholarItem
                        
        if isinstance(item,GScholarCitationItem):
            #process CitationItem
            
            citationItem = {
                            'authors' : item['authors'],
                            'title' : item['title']
                            }
            #authors = item['authors']
            #title = item['title']
            #publisher = item['publisher']
            #times_cited = item['citedBy']
            #abstract = item['abstract']
            #year = item['pubDate']
            
            self.cursor.execute("SELECT count(*) from publications where title = '%s'" % item['title'])
            numRows = self.cursor.fetchone()
            
            if(numRows[0] == 0):
                self.cursor.execute("""INSERT INTO publications (authors,title) VALUES
                                    ('%(authors)s', '%(title)s'')""",
                                    citationItem)
                
                #self.cursor.execute("INSERT INTO publications (title,authors,publisher,times_cited,pub_date) VALUES ('%s', '%s', '%s', '%s', '%s')"
                #                    % (title,authors,publisher,times_cited,year))
                                                    
        return item
    
    def close_pider(self, spider):
        self.file.write('\n</author>')
        self.file.close()

        


