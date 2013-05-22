import csv
import MySQLdb


def getSearchNames(name,surname,middleName,secondSurname):
    result = surname + ' ' + name + ';'                                                 # Doe John
    result += surname + ' ' + name[0]                                                   # Doe J
    if middleName and secondSurname:
        result += ';' + surname + ' ' + secondSurname[0] + name[0] + middleName[0] + ';'# Doe SJS
        result += surname + '-' + secondSurname + ' ' + name[0] + middleName[0]         # Doe-Smith JS

    if middleName:
        result += ';' + surname + ' ' + name[0] + middleName[0]                         # Doe JS
    if secondSurname: 
        result += ';' + surname + ' ' + secondSurname[0] + name[0] + ';'                # Doe SJ
        result += surname + ' ' + secondSurname + ' ' + name + ';'                      # Doe Smith John
        result += surname + '-' + secondSurname + ' ' + name + ';'                      # Doe-Smith John
        result += surname + '-' + secondSurname + ' ' + name[0]                         # Doe-Smith J
        
    return MySQLdb.escape_string(result)





mydb = MySQLdb.connect('localhost','supm', 'supm', 'supmdb')

mydb.autocommit(True)

mydb.set_character_set('utf8')

cursor = mydb.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')


csv_data = csv.reader(file('DIA.csv'))

for row in csv_data:
    
    row[11] = getSearchNames(row[3],row[1],row[4],row[2])
    
    print row
    
    for item in row:
        item.encode('utf-8')

    cursor.execute("INSERT INTO authors (code, surname, second_surname, name, middle_name, gscholar_id, wok_id, scopus_id, category, department, email, search_names) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row)
#close the connection to the database.
cursor.close()
print "Done"