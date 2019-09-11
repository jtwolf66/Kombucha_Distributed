import mysql.connector
from mysql.connector import errorcode
import os 

hostinfo = os.environ['MYSQLCONNECT']

try:
	cnx = mysql.connector.connect(user='root', password='password',
								  host=hostinfo)
except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with your user name or password")
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exist")
	else:
		print(err)
else:
	cnx.close()

cursor = cnx.cursor()

TABLES = {}
DB_NAME = 'Kombucha'

TABLES['Kombucha_Data'] = (
	"CREATE TABLE `Kombucha_Data` ("
	"  `Time` date NOT NULL,"
	"  `Batch` int(127) NOT NULL,"
	"  'Heater_State int(2) NOT NULL,"
	"  `Temperature` REAL(53) NOT NULL,"
	"  `Ambient_Temperature` REAL(53) NOT NULL,"
	"  `Ambient_Humidity` REAL(53) NOT NULL,"
	"  `pH` REAL(53) ,"
	"  PRIMARY KEY (`Batch`)"
	") ENGINE=InnoDB")

# Startup Script
def create_database(cursor):
	try:
		cursor.execute(
			"CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
	except mysql.connector.Error as err:
		print("Failed creating database: {}".format(err))
		exit(1)

try:
	cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
	print("Database {} does not exists.".format(DB_NAME))
	if err.errno == errorcode.ER_BAD_DB_ERROR:
		create_database(cursor)
		print("Database {} created successfully.".format(DB_NAME))
		cnx.database = DB_NAME
	else:
		print(err)
		exit(1)


for table_name in TABLES:
	table_description = TABLES[table_name]
	try:
		cursor.execute(table_description)
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
			print("already exists.")
		else:
			print(err.msg)
	else:
		print("OK")

cursor.close()
cnx.close()
