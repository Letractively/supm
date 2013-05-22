from suds.client import Client
from suds.client import WebFault
import math
import xml.etree.ElementTree as ET

import MySQLdb

#Function extractRecords
#Params: xmlResults - xml formated records results from the soap web service response
#returns: mysqlQuer - The query with the inserts to the database
def extractRecords(xmlResults):
    
    #Strip the xmlns attribute from the "records" tag
    nameSpace = ' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"'
    xmlResults = xmlResults.replace(nameSpace, '')
    
    global insertValues 
    tree = ET.fromstring(xmlResults)
    
    records = tree.findall('.//REC')
    global recordsProcessed
    
    recordsProcessed = 1

    for record in records:
        
        query = 'INSERT INTO publications (title,authors,pub_type,pub_date,publisher,doc_type,abstract,times_cited) VALUES '
        
        staticData = record.find('.//static_data')
        
        #TITLE
        paperTitle = staticData.find('.//title[@type="item"]')
        if paperTitle is None:
            insertValues = 'null,'
        else:
            insertValues = '"' + MySQLdb.escape_string(paperTitle.text) + '",'
        
        #AUTHORS
        autores = ''
        for author in staticData.findall('.//summary/names/name[@role="author"]/display_name'):
            autores += ' -' + author.text
            
        if autores == '':
            insertValues += 'null,'
        else:
            insertValues += '"' + MySQLdb.escape_string(autores) + '",' 
        
        #PUB_TYPE 
        #PUB_DATE
        pubInfo = staticData.find('.//pub_info')
        if pubInfo is not None:
            insertValues += '"' + MySQLdb.escape_string(pubInfo.attrib['pubtype']) + '",'
            insertValues += '"' + MySQLdb.escape_string(pubInfo.attrib['pubyear']) + '",'
        else:
            insertValues += 'null,null,'
            
        #PUBLISHER
        pubs = ''
        for publishers in staticData.findall('.//publishers/publisher'):
            publisherName = publishers.find('.//full_name')
            pubs += publisherName.text + ' '
        if pubs == '':
            insertValues += 'null,'
        else:
            insertValues += '"' + MySQLdb.escape_string(pubs) + '",'
         
        #DOC_TYPE   
        docType = staticData.find('.//doctype')
        if docType is not None:
            insertValues +=  '"' + MySQLdb.escape_string(docType.text) + '",'
        else:
            insertValues += 'null,'
        
        #ABSTRACT
        abstract = staticData.find('.//abstract_text/p')
        if abstract is not None:
            insertValues += '"' + MySQLdb.escape_string(abstract.text) + '",'
        else:
            insertValues += 'null,'
            
        dynamicData = record.find('.//dynamic_data')
        
        #TIMES_CITED
        timesCited = dynamicData.find('.//silo_tc')
        if timesCited is not None:
            insertValues += timesCited.attrib['local_count']
        else:
            insertValues += 'null'
        
        #putting all the query together
        
        query += '(' + insertValues + ')'
        recordsProcessed += 1
        
        insertIntoDatabase(query, paperTitle.text)
#End function extractRecords



#Function insertintoDatabase
def insertIntoDatabase(query,pubTitle):
    
    mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
    
    mydb.autocommit(True)
    
    mydb.set_character_set('utf8')
    
    cursor = mydb.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    
    cursor.execute("SELECT count(*) from publications where title = %(title)s", dict(title = pubTitle))
    numRows = cursor.fetchone()
    
    if (numRows[0] == 0):
        cursor.execute(query)
    
    cursor.close()
    
#End function insertIntoDatabase






authURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
searchURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
searchLiteURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl'

c = Client(authURL)
result = c.service.authenticate()
print 'Authenticated\n'
c.set_options(headers={'Cookie':'SID="'+result+'"'})

client = Client(searchURL, headers={'Cookie':'SID="'+result+'"'})



queryParams = client.factory.create('queryParameters')
queryParams['databaseId'] = 'WOS'
queryParams['queryLanguage'] = 'en'
queryParams['userQuery'] = 'AU=(larranaga P)'

retParams = client.factory.create('retrieveParameters')

retParams['firstRecord'] = 1
retParams['count'] = 100


try:
    print 'Searching...\n'
    
    #retrieve the first results
    result = client.service.search(queryParams, retParams)
    extractRecords(result['records'])
    
    recordsCount = result['recordsFound']
    #Since WOK limits the amount of results to 100 there is a need
    #to retrieve all the results if the query results count is bigger than 100
    if recordsCount > 100:
        print "Extracting..."
        for x in range(1,int(math.ceil(result['recordsFound']/100.0))):
            retParams['firstRecord'] = (x*100)+1
            result = client.service.retrieve(result['queryId'],retParams)
            
            #EXTRACT records from xml and insert into the database
            extractRecords(result['records'])

    print 'Closing'
    c.service.closeSession()
    
except WebFault, e:
    print e




#print result

#queryParams = client.factory.create('retrieveParameters')
#print queryParams
