import json
import urllib2
import re 
from datetime import datetime


data = urllib2.urlopen('http://searchapi.scopus.com/documentSearch.url?apiKey=e216a9f5c60ecf6f105ba5225a09f99b&search=AU-ID(7004720416)&numResults=200')

data = data.read()

data = re.search('null\((.+)\)',data).group(1)
j = json.loads(data)
count = 0
for pub in j['OK']['results']:
    count += 1
    print '\n Publication N: ' + str(count)
    print pub['title']
    print pub['doctype'] #In the database we refer to this item as publication type (journal, Book,etc.)
    print pub['citedbycount']
    print pub['eid']
    print pub['inwardurl']
    print str(datetime.strptime(pub['pubdate'],'%Y-%m-%d').year)
   
