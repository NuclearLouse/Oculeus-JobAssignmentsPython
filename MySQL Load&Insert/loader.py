from mysql.connector import MySQLConnection, Error
from mysql_dbconfig import read_db_config
import time


db_config = read_db_config()
conn = MySQLConnection(**db_config)
cursor = conn.cursor()

start_time = time.time()
query = "LOAD DATA INFILE 'c:/ProgramData/MySQL/MYSQL Server 8.0/Data/destinations/destination.csv' \
    INTO TABLE code_destination FIELDS TERMINATED BY ';'  LINES TERMINATED BY '\r\n' IGNORE 1 LINES (code, destination)"
cursor.execute(query)
conn.commit()

print("Операция заняла : %s секунд" % (time.time() - start_time))