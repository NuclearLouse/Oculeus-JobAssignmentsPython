import csv
import time
from mysql.connector import MySQLConnection, Error
from mysql_dbconfig import read_db_config

db_config = read_db_config()
conn = MySQLConnection(**db_config)
cursor = conn.cursor()

with open('destination.csv', "r") as file:
    datareader = file.readlines()

start_time = time.time()
for row in datareader:
    data = row.split(';')
    #print(data[0], '  ', data[1])
    query = "INSERT INTO code_destination(code, destination) VALUES('" + data[0] + "','" + data[1] + "')"
    cursor.execute(query)
conn.commit()
print("Операция заняла : %s секунд" % (time.time() - start_time))