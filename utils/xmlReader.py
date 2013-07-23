import xml.etree.ElementTree as ET
tree = ET.parse('results.xml')


for record in tree.findall('.//REC'):
    for staticData in record.findall('.//static_data'):
        paperTitle = staticData.find('.//title[@type="item"]').text
        print "\nTitulo: "+paperTitle
        
        
        print "Autores:"
        for author in staticData.findall('.//summary/names/name[@role="author"]/display_name'):
            print "   -" + author.text
        
        
        pubInfo = staticData.find('.//pub_info')
        print "Publisher data"
        print "Type: " + pubInfo.attrib['pubtype']
        print "Year: " + pubInfo.attrib['pubyear']
        
        print "Publisher Names:"
        for publishers in staticData.findall('.//publishers/publisher'):
            publisherName = publishers.find('.//full_name').text
            print "    -"+publisherName
        docType = staticData.find('.//doctype').text
        print "Document Type: " + docType
        
        abstract = staticData.find('.//abstract_text/p').text
        print "Abstract: "+ abstract
        
    dynamicData = record.find('.//dynamic_data')
    
    timeCited = dynamicData.find('.//silo_tc').attrib['local_count']
    print "Times Cited: " + timeCited
    
    


    
    




