# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import MySQLdb

from supm.items import GScholarCitationItem, ScopusCitationItem

class SupmPipeline(object):
    def process_item(self, item, spider):
        return item

class publicationsPipeline(object):

    def __init__(self):
        self.db = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
        self.db.autocommit(True)
        self.cursor = self.db.cursor()
        self.db.set_character_set('utf8')
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')
        
        self.authID = ''
        self.pubID = ''
        
        
    def process_item(self,item,spider):
        
        #setting the author id so it can be associated with the publication
        self.authID = str(item['authorId'])
        
        #process Google Scholar Citation Item
        if isinstance(item,GScholarCitationItem):
        
            self.citationItem = {
                            'all_authors' : item['authors'],
                            'title' : item['title'],
                            'publisher': item['publisher'],
                            'times_cited': item['citedBy'],
                            'pub_date': item['pubDate'],
                            'abstract': item['abstract'],
                            'pub_url': item['pubUrl'],
                            'doc_uid': item['docUID'],
                            'source': item['source'],
                            }
            
        elif isinstance(item, ScopusCitationItem):
            self.citationItem = {
                            'title' : item['title'],
                            'times_cited': item['citedBy'],
                            'pub_date': item['pubDate'],
                            'pub_url': item['pubUrl'],
                            'doc_uid': item['docUID'],
                            'pub_type': item['pubType'],
                            'source': item['source'],
                            }
            
        #Verify if the title exists
        self.cursor.execute(u"SELECT id, times_cited from publications where doc_uid = %s", item['docUID'])
        row = self.cursor.fetchone()
        
        
            
        if row is None:
            #Title does not exists, proceed to insert publication in DB
            if isinstance(item, GScholarCitationItem):
                self.cursor.execute('INSERT INTO publications (all_authors,title,publisher,times_cited,pub_date,source,abstract,pub_url,doc_uid) VALUES \
                                (%(all_authors)s, %(title)s, %(publisher)s, %(times_cited)s, %(pub_date)s, %(source)s, %(abstract)s, %(pub_url)s, %(doc_uid)s)',
                                self.citationItem)
                
            elif isinstance(item, ScopusCitationItem):
                self.cursor.execute('INSERT INTO publications (title,times_cited,pub_date,source,pub_url,doc_uid,pub_type) VALUES \
                                (%(title)s, %(times_cited)s, %(pub_date)s, %(source)s, %(pub_url)s, %(doc_uid)s, %(pub_type)s)',
                                self.citationItem)
            
            #Associate with the author
            self.pubID = MySQLdb.escape_string(str(self.cursor.lastrowid))
            self.cursor.execute('INSERT INTO  publications_authors (author_id, publication_id) VALUES (%s,%s)' % (self.authID, self.pubID))
            
        else:
            #if title already exists
            
            #Save the publiction id for association with the author 
            #and the times_cited for checking new citations
            self.pubID = MySQLdb.escape_string(str(row[0]))
            timesCitedOLD = row[1]
            
            #Check if the publication is already associated with the author
            self.cursor.execute('SELECT id from publications_authors WHERE publication_id = %s AND author_id = %s' % (self.pubID, self.authID))
            row = self.cursor.fetchone()
            
            if row is None:
                #Title exists but is not associated with the author
                self.cursor.execute('INSERT INTO  publications_authors (author_id, publication_id) VALUES (%s,%s)' % (self.authID, self.pubID))
            
            else:
                #if the title is already associated with the author
                #Check if there are no new citations for the publication
                timesCitedNEW = long(item['citedBy'])
                
                if  timesCitedNEW > timesCitedOLD :
                    #If there is a new citation update the publication times_cited
                    self.cursor.execute('UPDATE publications SET times_cited = %s WHERE id = %s' % (str(timesCitedNEW), self.pubID))
            
        return item