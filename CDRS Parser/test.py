#!/usr/bin/python3
#-*- coding: utf-8 -*-
from mysql_dbconfig import read_db_config
from mysql.connector import MySQLConnection

db_config = read_db_config()
conn = MySQLConnection(**db_config)
cursor = conn.cursor()
query = "CREATE SCHEMA `test_schema`;"
cursor.execute(query)
conn.commit()