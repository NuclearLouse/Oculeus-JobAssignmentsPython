import sys
import time
from mysql.connector import MySQLConnection, Error
from mysql_dbconfig import read_db_config


if len(sys.argv) == 1 or len(sys.argv) > 2:
    print("Invalid argument passed!")
    sys.exit(0)

query = "SELECT code, destination FROM code_destination"
db_config = read_db_config()
conn = MySQLConnection(**db_config)
cursor = conn.cursor()
cursor.execute(query)
destination = cursor.fetchall()
destinations = {}
for row in destination:
    destinations[row[0]] = row[1]

number = sys.argv[1]
x = len(number)
find = False
start_time = time.time()
print(start_time)
for i in range(0,x):
    code = int(number[:x-i])
    try:
        dst = destinations[code]
        print(code, ' = ', dst)
        find = True
        break
    except:
        pass

if not find:
    print('Destination does not exist!')
print(time.time())
print("Поиск по методу try, занял %s секунд " % (time.time() - start_time))


