import timeit
from random import randint

numbers = []
for i in range(500000):
    number = randint(1, 100000000000)
    numbers.append(number)

f = open('numbers.txt', 'w')
for num in numbers:
    print(num, file=f)
f.close()

setup_code = """\
from mysql.connector import MySQLConnection, Error
from mysql_dbconfig import read_db_config

query = "SELECT code, destination FROM code_destination"
db_config = read_db_config()
conn = MySQLConnection(**db_config)
cursor = conn.cursor()
cursor.execute(query)
destination = cursor.fetchall()
destinations = {}
for row in destination:
    destinations[row[0]] = row[1]

f = open('numbers.txt', 'r')
numbers = f.read()
counter = 0
"""
mycode_try = """\
for num in numbers:
    number = str(num)
    x = len(number)
    for i in range(0,x):
        code = number[:x-i]
        try:
            dst = destinations[code]
            counter += 1
            break
        except:
            continue
print("Numbers: ", counter, "  time: ", end = '')
"""
mycode_ifin = """\
for num in numbers:
    number = str(num)
    x = len(number)
    for i in range(0,x):
        code = number[:x-i]
        if code in destinations:
            dst = destinations[code]
            counter += 1
            break
print("Numbers: ", counter, "  time: ", end = '')
"""

code_concat = """\
for num in numbers:
    nummber = str(num)
    query = "SELECT * FROM code_destination WHERE '" + number +\
        "' LIKE CONCAT ( code_destination.code, '%') order by code desc limit 1"

    db_config = read_db_config()
    conn = MySQLConnection(**db_config)
    cursor = conn.cursor()
    cursor.execute(query)
    destination = cursor.fetchall()


print(destination[0][1],' = ', destination[0][2])
"""
print (timeit.timeit(setup = setup_code, stmt = mycode_try, number = 1))
print (timeit.timeit(setup = setup_code, stmt = mycode_ifin, number = 1))