
import MySQLdb

mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')

mydb.autocommit(True)

mydb.set_character_set('utf8')

cursor = mydb.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')
cursor.execute("SELECT count(*) from publications where id = 1121")
result = cursor.fetchone()


print result[0]
#close the connection to the database.
cursor.close()
print "Done"