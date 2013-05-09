import csv
import MySQLdb

mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')

mydb.autocommit(True)

mydb.set_character_set('utf8')

cursor = mydb.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')


csv_data = csv.reader(file('DIA.csv'))

for row in csv_data:
    
    for item in row:
        item.encode('utf-8')

    cursor.execute("INSERT INTO authors (code, surname, second_surname, name, middle_name, category, department, email, gscholar_id ) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", row)
#close the connection to the database.
cursor.close()
print "Done"