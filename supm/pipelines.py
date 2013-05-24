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
        self.authID = ''
        self.pubID = ''
        
        
    def process_item(self,item,spider):
        
        #setting the author id so it can be associated with the publication
        self.authID = MySQLdb.escape_string(str(item['authorId']))
        
        #process Google Scholar Citation Item
        if isinstance(item,GScholarCitationItem):
        
            
            citationItem = {
                            'all_authors' : item['authors'],
                            'title' : str(MySQLdb.escape_string(item['title'])),
                            'publisher': item['publisher'],
                            'times_cited': item['citedBy'],
                            'pub_date': item['pubDate'],
                            'abstract': str(MySQLdb.escape_string(item['abstract'])),
                            'pub_url': MySQLdb.escape_string(item['pubUrl'])
                            }
            
            self.cursor.execute("SELECT id from publications where title = %(title)s", dict(title = item['title']))
            row = self.cursor.fetchone()
            
            if row is None:
                self.cursor.execute('INSERT INTO publications (all_authors,title,publisher,times_cited,pub_date,source,abstract,pub_url) VALUES \
                                    (%(all_authors)s, %(title)s, %(publisher)s, %(times_cited)s, %(pub_date)s, "Google Scholar", %(abstract)s, %(pub_url)s)',
                                    citationItem)
                self.pubID = MySQLdb.escape_string(str(self.cursor.lastrowid))
                self.cursor.execute("INSERT INTO  publications_authors (author_id, publication_id) VALUES (%s,%s)" % (self.authID, self.pubID))
            else:
                #Title already exists
                self.pubID = MySQLdb.escape_string(str(row[0]))
                self.cursor.execute("INSERT INTO  publications_authors (author_id, publication_id) VALUES (%s,%s)" % (self.authID, self.pubID))
            
            #Populating the table authors_has_publications to associate the authors with their papers
            
                
   

        return item