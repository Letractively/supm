from suds.client import Client
from suds.client import WebFault
import math
import xml.etree.ElementTree as ET
from test import timeCited


#Function extractRecords
#Params: xmlResults - xml formated records results from the soap web service response
#returns: mysqlQuer - The query with the inserts to the database
def extractRecords(xmlResults):
    
    #Strip the xmlns attribute from the "records" tag
    nameSpace = ' xmlns="http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"'
    xmlResults = xmlResults.replace(nameSpace, '')
    query = 'INSERT INTO [table] (f1,f2,f3,f4...) VALUES '
    global insertValues 
    tree = ET.fromstring(xmlResults)
    
    records = tree.findall('.//REC')
    global recordsProcessed
    
    recordsProcessed = 1

    for record in records:
        
        staticData = record.find('.//static_data')
        
        paperTitle = staticData.find('.//title[@type="item"]')
        if paperTitle is None:
            insertValues = 'null,'
        else:
            insertValues = '"' + paperTitle.text + '",'
        
        autores = ''
        for author in staticData.findall('.//summary/names/name[@role="author"]/display_name'):
            autores += " -" + author.text
            
        if autores == '':
            insertValues += 'null,'
        else:
            insertValues += '"' + autores + '",' 
        
        pubInfo = staticData.find('.//pub_info')
        if pubInfo is not None:
            insertValues += pubInfo.attrib['pubtype'] + ','
            insertValues += pubInfo.attrib['pubyear'] + ','
        else:
            insertValues += 'null,null,'
            
        
        pubs = ''
        for publishers in staticData.findall('.//publishers/publisher'):
            publisherName = publishers.find('.//full_name')
            pubs += publisherName.text + ' '
        if pubs == '':
            insertValues += 'null,'
        else:
            insertValues += pubs + ','
            
        docType = staticData.find('.//doctype')
        if docType is not None:
            insertValues = insertValues + docType.text + ','
        else:
            insertValues += 'null,'
        
        abstract = staticData.find('.//abstract_text/p')
        if abstract is not None:
            insertValues += '"' + abstract.text + '",'
        else:
            insertValues += 'null,'
            
        dynamicData = record.find('.//dynamic_data')
        
        timesCited = dynamicData.find('.//silo_tc')
        if timesCited is not None:
            insertValues += timesCited.attrib['local_count']
        else:
            insertValues += 'null'
        
        #putting all the query together
        if len(records) == recordsProcessed:
            query += '(' + insertValues + ')'
        else:
            query += '(' + insertValues + '),'
            recordsProcessed += 1
                
    return query
#End function extractRecords







authURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
searchURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
searchLiteURL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl'

c = Client(authURL)
result = c.service.authenticate()
print 'authenticated\n'
c.set_options(headers={'Cookie':'SID="'+result+'"'})

client = Client(searchURL, headers={'Cookie':'SID="'+result+'"'})



queryParams = client.factory.create('queryParameters')
queryParams['databaseId'] = 'WOS'
queryParams['queryLanguage'] = 'en'
queryParams['userQuery'] = 'AU=(larra?aga P)'

retParams = client.factory.create('retrieveParameters')

retParams['firstRecord'] = 1
retParams['count'] = 100


try:
    print 'search\n'
    
    #retrieve the first results
    result = client.service.search(queryParams, retParams)
    extractRecords(result['records'])
    
    recordsCount = result['recordsFound']
    #Since WOK limits the amount of results to 100 there is a need
    #to retrieve all the results if the query results count is bigger than 100
    if recordsCount > 100:
        for x in range(1,int(math.ceil(result['recordsFound']/100.0))):
            retParams['firstRecord'] = (x*100)+1
            result = client.service.retrieve(result['queryId'],retParams)
            print extractRecords(result['records'])

    print 'closing\n'
    c.service.closeSession()
    
except WebFault, e:
    print e




#print result

#queryParams = client.factory.create('retrieveParameters')
#print queryParams
