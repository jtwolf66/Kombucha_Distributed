#!/usr/bin/python
import mysql.connector
import glob
import os
from datetime import date, datetime
from mysql.connector import errorcode
hostinfo = os.environ['MYSQLCONNECT']
##################################################
#
# This code is run by a cron-job every 5 minutes.
#
##################################################



##################################################
# Database Setup
##################################################

try:
	cnx = mysql.connector.connect(user='root', password='password',
								  host=hostinfo,database='Kombucha')
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

##################################################
# Useful parameters
##################################################

#Working Directory
PWD=os.getcwd()

def write_to_db(cursor):
	"""Writes batch, time, temperature, ambient temperature, and humidity to database"""
	cur_time = datetime.now()
	cursor.execute('''INSERT INTO Kombucha_Data('Time', 'Batch', 'Heater State', 'Temperature', 'Ambient Temperature', 'Ambient Humidity','pH')
				  VALUES(?,?,?,?,?,?,NULL)''', (cur_time, 1, 1, 32.1, 31.2, 34.3))
	cursor.commit()
	return

write_to_db(cursor)
##################################################

##################################################
# Define switching state
##################################################
