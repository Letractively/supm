# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import MySQLdb
import re

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
        
            #Strip the last part or the URL to get the document URI
            doc_uid = re.match('(.*)(:)(.*)',item['pubUrl']).group(3)
            
            if item['citedBy'] == "":
                item['citedBy'] = "0"
            
            citationItem = {
                            'all_authors' : item['authors'],
                            'title' : str(MySQLdb.escape_string(item['title'])),
                            'publisher': item['publisher'],
                            'times_cited': item['citedBy'],
                            'pub_date': item['pubDate'],
                            'abstract': str(MySQLdb.escape_string(item['abstract'])),
                            'pub_url': MySQLdb.escape_string(item['pubUrl']),
                            'doc_uid': MySQLdb.escape_string(doc_uid),
                            }
            
            self.cursor.execute("SELECT id, times_cited from publications where doc_uid = %s", MySQLdb.escape_string(doc_uid))
            row = self.cursor.fetchone()
            
            if row is None:
                #Title does not exists, proceed to insert publication in DB
                self.cursor.execute('INSERT INTO publications (all_authors,title,publisher,times_cited,pub_date,source,abstract,pub_url,doc_uid) VALUES \
                                    (%(all_authors)s, %(title)s, %(publisher)s, %(times_cited)s, %(pub_date)s, "Google Scholar", %(abstract)s, %(pub_url)s, %(doc_uid)s)',
                                    citationItem)
                self.pubID = MySQLdb.escape_string(str(self.cursor.lastrowid))
                self.cursor.execute("INSERT INTO  publications_authors (author_id, publication_id) VALUES (%s,%s)" % (self.authID, self.pubID))
            else:
                #Title already exists
                self.pubID = MySQLdb.escape_string(str(row[0]))
                timesCitedOLD = row[1]
                self.cursor.execute('SELECT id from publications_authors WHERE publication_id = %s AND author_id = %s' % (self.pubID, self.authID))
                row = self.cursor.fetchone()
                if row is None:
                    #Title exists but is not associated with the author
                    self.cursor.execute("INSERT INTO  publications_authors (author_id, publication_id) VALUES (%s,%s)" % (self.authID, self.pubID))
                else:
                    #Check if there are no new citations for the publication
                    timesCitedNEW = long(item['citedBy'])
                    if  timesCitedNEW > timesCitedOLD :
                        self.cursor.execute("UPDATE publications SET times_cited = %s WHERE id = %s" % (MySQLdb.escape_string(str(timesCitedNEW)), self.pubID))
            
        return item