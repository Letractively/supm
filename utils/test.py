import re
import MySQLdb

def executeMysql(cadena):
    
    print type(cadena)
    mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')
    mydb.autocommit(True)
    mydb.set_character_set('utf8')
    
    cursor = mydb.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    
    cadena = cadena.encode('utf-8')
    
    cursor.execute(u"UPDATE publications set title='"+MySQLdb.escape_string(cadena)+"' where id=1564")
    
    cursor.execute("SELECT title from publications where id=1564")
    #close the connection to the database.
    row = cursor.fetchone() 
    
    cursor.close()
    
    return row




url = "http://scholar.google.es/citations?view_op=view_ciINSPEC:10854926tation&=======hl=es&user=w62izrcAAAAJ&citation_for_view=w62izrcAAAAJ:u-x6o8ySG0sC"

tag = '<a style="text-decoration:none" href="http://www.dia.fi.upm.es/~ocorcho/documents/EON2003_CorchoEtAl.pdf">2 nd International Workshop on Evaluation of Ontology-based Tools</a>'
tag1 = '2 nd International INSPEC:19212099210 Workshop on Evaluation of Ontology-based Tools'
tag2 = 'null({"OK":{"position":"0","results":[{"abs":"","affiliation":"","authlist":"","citedbycount":"0","doctype":"Journal","doi":"10.1016/j.pscychresns.2012.06.001","eid":"2-s2.0-84879460078","firstauth":"Morales, D.A.","inwardurl":"http://www.scopus.com/inward/record.url?partnerID=HzOxMe3b&scp=84879460078","issn":"09254927","issue":"2","page":"92-98","pubdate":"2013-08-30","scp":"84879460078","sourcetitle":"Psychiatry Research - Neuroimaging","title":"Predicting dementia development in Parkinson\'s disease using Bayesian network classifiers","vol":"213"}})'

chino = u'\u30b3\u30f3\u30d7\u30ed\u30de\u30a4\u30ba\u30fb\u30d7\u30ed\u30b0\u30e9\u30df\u30f3\u30b0\u306b\u57fa\u3065\u304f\u30de\u30c9\u30ea\u30fc\u30c9\u9996\u90fd\u570fu\u30b3\u30f3\u30d7\u30ed\u30de\u30a4\u30ba\u30fb\u30d7\u30ed\u30b0\u30e9\u30df\u30f3\u30b0\u306b\u57fa\u3065\u304f\u30de\u30c9\u30ea\u30fc\u30c9\u9996\u90fd\u570f'

result = re.match('(.*)(=)(.+)',url).group(3)


result = re.search('null\((.+)\)',tag2).group(1)


chino2 = u'\u30ad\u30e3\u30ea\u30d6\u30ec\u30fc\u30b7\u30e7\u30f3\u306a\u3057\u306e\u52d5\u753b\u50cf\u306e 3 \u6b21\u5143\u89e3\u6790'

#result = executeMysql(chino2)

espanol = u"Une m\xe9thode de d\xe9bogage d'ontologies OWL bas\xe9es sur la d\xe9tection d'anti-patrons"



print executeMysql(espanol)[0]



#print chino.encode('utf-8')


#print result 
#result = re.match('(<a.*>)(.*)(</a>)',tag).group(2)
#result1 = re.match('(<a.*>)(.*)(</a>)',tag1).group(2)

#if result1 is None:
#    print tag1
#else:
#    print result
    
    
#if "INSPEC" not in url:
#    print "NO ESTA"
#else :
#    print "SI ESTA"
