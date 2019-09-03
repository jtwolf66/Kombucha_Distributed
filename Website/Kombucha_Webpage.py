# import things
from flask import Flask, request
from flask_table import Table, Col
import Adafruit_DHT
import RPi.GPIO as GPIO
import os
import glob
from datetime import date, datetime

#######################
# This code desperately needs refactoring, but is a functional homebrew solution
#######################

app = Flask(__name__)


##################################################
# Database Setup
##################################################

try:
	cnx = mysql.connector.connect(user='wolf', password='wolfdb',
							      host='127.0.0.1',database='Kombucha_data')
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

#######################
# Database Functions
#######################

def write_to_db(batch_num,pH,cursor):
	"""Writes batch, time, temperature, ambient temperature, and humidity to database"""

	#Batch Number
	batch = 1

	# GPIO pin number to control heating pad
	heat_pin = 19
	amb_heat_pin = 22

	# Define minimum and maximum temperatures (deg. C)
	min_temp = 24.0
	max_temp = 27.0

	# Serial prefix for DS1820 probe.
	ds1820_prefix = '28'

	##################################################
	# System-specific stuff for DS1820 temp probe. 
	##################################################
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(heat_pin, GPIO.OUT)

	os.system('modprobe w1-gpio')
	os.system('modprobe w1-therm')

	base_dir = '/sys/bus/w1/devices/'

	device_folder = glob.glob(base_dir + ds1820_prefix + '*')[0]
	device_file = device_folder + '/w1_slave'

	#######################
	# Sensor Functions
	#######################

	def read_temp_raw():
		with open(device_file, 'r') as deviceFile:
			lines = deviceFile.readlines()
		return lines

	def read_temp():
		"""Reads device file and returns temperature in deg. Celcius"""
		lines = read_temp_raw()
		while lines[0].strip()[-3:] != 'YES':
			time.sleep(0.2)
			lines = read_temp_raw()
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos+2:]
			return float(temp_string) / 1000.0

	def read_ambient(sensor_id,pin):
		sensor_args = { '11': Adafruit_DHT.DHT11,
					'22': Adafruit_DHT.DHT22,
					'2302': Adafruit_DHT.AM2302 }
		if sensor_id in sensor_args:
			sensor = sensor_args[sensor_id]
			amb_hum, amb_temp = Adafruit_DHT.read_retry(sensor, pin)
			return amb_hum, amb_temp
		else:
			print('Failed to get reading. Invalid sensor_id')
			return

	def check_heater_state():
		return GPIO.input(heat_pin)
		

	cur_time = datetime.now()
	heater_state = check_heater_state()
	temp = read_temp()
	amb_hum, amb_temp = read_ambient(amb_heat_pin,2)

	cursor.execute('''INSERT INTO Kombucha_Data('Time', 'Batch', 'Heater State', 'Temperature', 'Ambient Temperature', 'Ambient Humidity','pH')
                  VALUES(?,?,?,?,?,?,NULL)''', (cur_time, batch_num, heater_state, temp, amb_temp, amb_hum))
	cursor.commit()
	return

def read_from_db(cursor):
	"""Writes batch, time, temperature, ambient temperature, and humidity to database"""
	cursor.execute('''SELECT * FROM (
		SELECT * FROM Kombucha_data ORDER BY Time DESC LIMIT 20)
		ORDER BY Time ASC;''')

	rows = cursor.fetchall()
	return rows

#######################
# Table Formatting
#######################

class ItemTable(Table):
	batch_num = Col('Batch')
	pH = Col('pH')
	cur_time = Col('Time')
	heater_state = Col('Heater State')
	temp = Col('Kombucha Temperature')
	amb_temp = Col('Ambient Temperature')
	amb_hum = Col('Ambient Humidity')


class Item(object):
	def __init__(self, info):
		(batch_num,cur_time,heater_state,temp,amb_temp,amb_hum,pH) = info
		self.batch_num = batch_num
		self.pH = pH
		self.cur_time = cur_time
		self.heater_state = heater_state
		self.temp = temp
		self.amb_temp = amb_temp
		self.amb_hum = amb_hum


def read_from_db(cursor):
	"""Writes batch, time, temperature, ambient temperature, and humidity to database"""
	cursor.execute('''SELECT * FROM (
		SELECT * FROM Kombucha_data ORDER BY Time DESC LIMIT 20)
		ORDER BY Time ASC;''')

	rows = cursor.fetchall()
	return rows

"""
#Convert to Items
items = []
rows = read_from_db()
print rows
for row in rows:
	items.append(Item(row))

# Populate the table
table = ItemTable(items)
"""

@app.route('/')
def homepage():
	#Creates a page with the table
	#Convert to Items
	items = []
	rows = read_from_db(cursor)
	print rows
	for row in rows:
		items.append(Item(row))

	# Populate the table
	table = ItemTable(items)

	return "<style> table, th, td {border: 1px solid black;} </style>" + table.__html__()

@app.route('/pH')
def pH_webpage():
	return '<head> <title>Input current pH</title> </head> <h2>Input current pH</h2><form method="POST"> <input name="pH_value"> <input type="submit"> </form> '

@app.route('/pH',methods=['POST'])
def pH_entry():
	pH_val = request.form.get('pH_value')
	print pH_val
	write_to_db(batch,float(pH_val),cursor)
	return 

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')