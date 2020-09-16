#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import logging
import logging.config
import os
import random
import sys
import time
from configparser import ConfigParser
from mysql.connector import MySQLConnection, Error
from mysql_dbconfig import read_db_config

class Table:
    """
    Class that implements all actions with tables.
    """
    def __init__(self, db_config, config_path):
        self.mydb = MySQLConnection(**db_config)
        self.cursor = self.mydb.cursor()
        self.config = ConfigParser()
        self.config.read(config_path)
        self.work_db = self.config.get('cdrs', 'working_db')
        self.template_db = self.config.get('cdrs', 'template_db')

    def show_table(self):
        """
        Checks for the existence of a template table.
        """
        template = True
        cdr = True
        query = "SHOW TABLES like 'template'"
        self.cursor.execute(query)
        tab = self.cursor.fetchall()
        if len(tab) == 0:
            template = False
        query = "SHOW TABLES like 'cdr_files'"
        self.cursor.execute(query)
        tab = self.cursor.fetchall()
        if len(tab) == 0:
            cdr = False
        return template and cdr

    def create_ini_tables(self):
        """
        Creates a template table.
        Creates a table with the names of checked files.
        """
        query = "CREATE TABLE cdr_files (id INT AUTO_INCREMENT PRIMARY KEY, name_files VARCHAR(45), name_table VARCHAR(45))"
        self.cursor.execute(query)
        query = "CREATE TABLE template (c1 DATE, c2 TIME, c3 VARCHAR(45), c4 INT(11), c5 VARCHAR(45), c6 INT(11), c7 VARCHAR(45), c8 VARCHAR(45))"
        self.cursor.execute(query)
        self.mydb.commit()

    def create_data_table(self):
        """
        Creates a table with selected data.
        """
        new_table = 'cpt_' + str(int(time.time())) + '_' + str(round(random.random()*100000))
        query = "CREATE TABLE " + self.work_db + '.' + new_table + " LIKE " + self.template_db + ".template"
        self.cursor.execute(query)
        self.mydb.commit()
        return new_table

    def check_name_files(self, file):
        """
        Checks if the file was processed before.
        """
        query = "SELECT name_table FROM cdr_files WHERE name_files ='" + file + "'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            name = str(rows[0][0])
            return False, name
        return True, ' '

    def write_files_table(self, file, name_table):
        """
        Enter the file name in the table of processed files.
        """
        query = "INSERT INTO " + self.template_db + ".cdr_files VALUES( id,'" + file + "','" + name_table + "')"
        self.cursor.execute(query)
        self.mydb.commit()

    def write_data_table(self, name_table, values):
        query = "INSERT INTO " + self.work_db + '.' + name_table + "(c1, c2, c3, c4, c5, c6, c7, c8)"+\
            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cursor.executemany(query, values)
        self.mydb.commit()

    def trunc_data_table(self, name_table, logger):
        """
        Clearing the existing table for rewriting.
        Or creating a table with the same name, if the table was accidentally deleted.
        """
        try:
            query = "TRUNCATE TABLE " + self.work_db + '.' + name_table
            print ("Clear table: ", name_table)
            self.cursor.execute(query)
            self.mydb.commit()
            return True

        except:
            print ("The source table was accidentally deleted!")
            print ("Create a table with the same name: ", name_table)
            logger.warning("Очистка не удалась. Таблицы нет. Создаю под именем %s" %name_table)
            query = "CREATE TABLE " + self.work_db + '.' + name_table + " LIKE " + self.template_db + ".template"
            self.cursor.execute(query)
            self.mydb.commit()
            return False



    def csv_file_reader(self, file_obj, name_table):
        """
        Read a csv file.
        Write selected data to txt file.
        And a call to write data to a table
        """
        reader = csv.reader(file_obj, delimiter=';')
        text = []
        for line in reader:
            string = [line[0], line[1], line[3], line[4], line[6], line[8], line[13], line[14]]
            text.append(string)
        self.write_data_table(name_table, text)

base_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_path, 'settings.ini')
logger = logging.getLogger('cdrParser')

if os.path.exists(config_path):
    config = ConfigParser()
    config.read(config_path)
    logging.config.fileConfig('settings.ini')
else:
    print("Config not found! Exiting!")
    sys.exit(1)

# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warning message')
# logger.error('error message')
# logger.critical('critical message')

if len(sys.argv) == 1:
    db_config = read_db_config()
    table = Table(db_config, config_path)
    source_path = config.get('cdrs', 'fold_original')
    backup_path = config.get('cdrs', 'fold_backup')
    if table.show_table() == False:
        logger.info("The program was started for the first time and without initialization.")
        print("Need initialization of tables.")
        print("Run the program with the key: -i or init")
        sys.exit(0)

    if len(os.listdir(source_path)) == 0:
        print("Source folder is empty!")
        logger.critical("Source folder is empty!")
        sys.exit(0)

    print("Initialization is not needed. Run the main script")
    logger.info("Run the main script.")
    #flag = True
    except_flag = False
    for file in os.listdir(source_path):
        logger.debug("Проверка %s в таблице имен" %file)
        check = table.check_name_files(file)
        if check[0]:
            logger.debug("Проверка вернула True и пустое имя. Такого файла еще не было")
            name_table = table.create_data_table()
        else:
            print("This file has already been processed")
            name_table = check[1]
            logger.debug("Проверка вернула False и имя %s Такой файл уже был" %name_table)
            logger.debug("Попытка очистки данных из таблицы")
            log = table.trunc_data_table(name_table, logger)
            if log:
                logger.debug("Таблица очистилась")
            #flag = check[0]

        with open(source_path + file) as f_obj:
            table.csv_file_reader(f_obj, name_table)
        logger.info("Запись файла %s в таблицу %s" %(file, name_table))
        print("Entered data from file: ", file)
        print("Transfer file to the backup folder")
        os.rename(source_path + file, backup_path + file)
        logger.warning("Переношу файл %s в бэкап папку" %file)
        if check[0]:
            logger.info("Внесение имени файла в таблицу имен")
            table.write_files_table(file, name_table)

    logger.critical("Обработаны все файлы. Папка пуста. Программа закрывается.")

if len(sys.argv) == 2:
    if sys.argv[1] == 'init' or sys.argv[1] == '-i':
        logger.warning("Start initialization. Create template table and file-names table")
        print("Start initialization")
        db_config = read_db_config()
        table = Table(db_config, config_path)
        table.create_ini_tables()
    else:
        print("Unknown parameter passed")
