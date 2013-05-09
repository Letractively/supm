# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import MySQLdb

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

        #process Google Scholar Citation Item
        if isinstance(item,GScholarCitationItem):
        
            
            citationItem = {
                            'authors' : item['authors'],
                            'title' : str(MySQLdb.escape_string(item['title'])),
                            'publisher': item['publisher'],
                            'times_cited': item['citedBy'],
                            'pub_date': item['pubDate'],
                            'abstract': str(MySQLdb.escape_string(item['abstract']))
                            }
            
            self.cursor.execute("SELECT count(*) from publications where title = %(title)s", dict(title = item['title']))
            numRows = self.cursor.fetchone()
            
            if (numRows[0] == 0):
                self.cursor.execute('INSERT INTO publications (authors,title,publisher,times_cited,pub_date,source,abstract) VALUES \
                                    (%(authors)s, %(title)s, %(publisher)s, %(times_cited)s, %(pub_date)s, "Google Scholar", %(abstract)s)',
                                    citationItem)
            else:
                print "##################################################"
                print "CITATION ALREADY EXISTS!!!!!!!:  %s" % item['title']
                print "##################################################"

        return item