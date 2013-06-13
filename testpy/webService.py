from suds.client import Client
from suds.client import WebFault
import math
import xml.etree.ElementTree as ET
import sys
import MySQLdb

#Function extractRecords
#Param: xmlResults - xml formated records results from the soap web service response
#returns: mysqlQuer - The query with the inserts to the database
def extractRecords(authorId,xmlResults):
    
    #Strip the xmlns attribute from the "records" tag
    nameSpace = ' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"'
    xmlResults = xmlResults.replace(nameSpace, '')
    
    global insertValues 
    tree = ET.fromstring(xmlResults)
    
    records = tree.findall('.//REC')
    print "ELEMENTS FOUND    "
    print len(records)

    for record in records:
        
        query = 'INSERT INTO publications (doc_uid,title,all_authors,pub_type,pub_date,publisher,doc_type,abstract,times_cited,source) VALUES ' 
        
        
        
        #Document Universal Identifier
        docUID = record.find('.//UID') 
        if docUID is None:
            print "FATAL ERROR: document without UID"
            sys.exit()
        else:
            insertValues = '"' + MySQLdb.escape_string(docUID.text) + '",'

        #Get the parent <static_data> tag
        staticData = record.find('.//static_data')
        
        #TITLE
        paperTitle = staticData.find('.//title[@type="item"]')
        if paperTitle is None:
            insertValues += 'null,'
        else:
            insertValues += '"' + MySQLdb.escape_string(paperTitle.text) + '",'
        
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
        
        #Get the partent <dynamic_data> tag    
        dynamicData = record.find('.//dynamic_data')
        
        #TIMES_CITED
        timesCited = dynamicData.find('.//silo_tc')
        if timesCited is not None:
            insertValues += timesCited.attrib['local_count']
        else:
            insertValues += '0'
        
        #putting all the query together
        query += '(' + insertValues + ',\'ISI WOK\')'
        
        insertIntoDatabase(query, authorId, docUID.text)
#End function extractRecords



#Function insertintoDatabase
def insertIntoDatabase(query, authorId, docUID):
    
    mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
    
    mydb.autocommit(True)
    
    mydb.set_character_set('utf8')
    
    cursor = mydb.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    
    authorId  = MySQLdb.escape_string(authorId)
    docUID = MySQLdb.escape_string(docUID)
    
    cursor.execute("SELECT id from publications where doc_uid = '%s'" % (docUID))

    row = cursor.fetchone()
    
    #If publication doesn't exist in DB
    if row is None:
        cursor.execute(query)
        publicationId = MySQLdb.escape_string(str(cursor.lastrowid))
        cursor.execute("INSERT INTO publications_authors (author_id, publication_id) VALUES (%s,%s)" % (authorId,publicationId))
    #If it exists save the publication ID to associate
    #to the author
    else:
        publicationId = MySQLdb.escape_string(str(row[0]))
        cursor.execute("SELECT id from publications_authors where publication_id = '%s' AND author_id = '%s'" % (publicationId, authorId))
        row = cursor.fetchone()
        if row is None:
            #The author is not yet associated with this publication
            cursor.execute("INSERT INTO publications_authors (author_id, publication_id) VALUES (%s,%s)" % (authorId,publicationId))
            
    cursor.close()
    
#End function insertIntoDatabase


#FUNCTION getDataFromWebService
#Function to get the data from the web service
#For each author ID this function will be executed
#reteriving all the publications for the provided ID
#Param: reseracherId: The author WOK id to be used for the query
def getDataFromWebService(researcherId,authorId):

    authURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
    searchURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
    searchLiteURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl'
    
    #Creating a web service client to retreive the SID
    #that will be used for executing queries in WOK
    c = Client(authURL)
    
    #getting the SID from the created web service client
    result = c.service.authenticate()
    
    print 'Authenticated\n'
    
    
    #c.set_options(headers={'Cookie':'SID="'+result+'"'})
    
    
    #including the SID into the web client query headers
    #THIS IS MANDATORY FOR THE WEB SERVICE CLIENT TO WORK
    client = Client(searchURL, headers={'Cookie':'SID="'+result+'"'})
    
    #Establishing the query parameters for the query
    queryParams = client.factory.create('queryParameters')
    queryParams['databaseId'] = 'WOS'
    queryParams['queryLanguage'] = 'en'
    queryParams['userQuery'] = 'AI=('+researcherId+')'
    
    #Specifying how many results will be returned per query
    #and what will be the first record returned (in this case 1)
    retParams = client.factory.create('retrieveParameters')
    retParams['firstRecord'] = 1
    retParams['count'] = 100
    
    
    try:
        print 'Searching...\n'
        
        #retrieve the first results
        result = client.service.search(queryParams, retParams)
        extractRecords(authorId,result['records'])
        
        #getting the total records count
        recordsCount = result['recordsFound']
        
        #Since WOK limits the amount of results to 100 there is a need
        #to retrieve all the results if the query results count is bigger than 100
        if recordsCount > 100:
            print "Extracting..."
            for x in range(1,int(math.ceil(result['recordsFound']/100.0))):
                retParams['firstRecord'] = (x*100)+1
                result = client.service.retrieve(result['queryId'],retParams)
                
                #EXTRACT records from xml and insert into the database
                extractRecords(authorId,result['records'])
                
        print 'Records Found: ' + str(recordsCount)
        print 'Closing'
        c.service.closeSession()
        
    except WebFault, e:
        print e

#End function getDataFromWebService


# FUNCTION getAuthorsData
#Functions that serves for getting 
#the necessary authors data to generate
#the queries to extract from the web service  
def getAuthorsData():
    
    #MUST CHANGE THIS to the correct parameters
    mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
    mydb.autocommit(True)
    mydb.set_character_set('utf8')
    cursor = mydb.cursor()
    cursor.execute("SELECT id, wok_id FROM authors")
    rows = cursor.fetchall()
    cursor.close()
    
    return rows

#END FUNCTION getAuthorData


#MAIN
for row in getAuthorsData():
    if row[1]:
        authorId = str(row[0])
        researcherId = str(row[1])
        print "Fetching data for author id: "+ str(authorId)
        getDataFromWebService(researcherId,authorId)













