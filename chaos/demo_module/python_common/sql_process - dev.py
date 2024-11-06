"""
Process SQL Folder

Takes all SQL files within the PROCESS subfolder.
No results or output expected. This is for ETL, Inserts, Deletes only.

[2019-03-18] Created the file.
[2019-04-05] Completed first draft
[2019-06-20] Logging and error checking added
[2019-08-18 | 01:16PM | David Colon] Added the creation of folders.
[2019-08-29 | 10:51AM | David Colon] Changed DB string to use INI File
[2019-12-17 | 09:28AM | David Colon] Added the option for continueing on failure for processing from the INI file.
2020-03-21 Converted to Class
"""

import os, sys
import pyodbc
import time
import datetime
import logging
from itertools import takewhile

class SqlProcess():

    def __init__(self, level='INFO'):
        self.log = ''
        self.line_format = logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(module)s] [%(funcName)s] %(message)s")
        self.log = logging.getLogger('__name__')
        self.log.setLevel(level)      
        self.error_count = 0
        self.files = []
        self.connection_string = ''
        self.start_time = time.time() # for timing the script

    # SET LOGGER
    def set_logger(self, new_logger, level='INFO'):
        self.log = new_logger
        self.log.setLevel(level)
    
    # SET CONNECTION STRING
    def set_connection_string(self, new_connection_string):
        self.connection_string = new_connection_string


    def get_text_from_file(self, filepath):
        # Get the text from SQL File
        fd = open(filepath)
        text = fd.read()
        fd.close
        return text

    def sql_file_execute(self, filepath):
        # Get SQL Text then send to execute
        sql_script = self.get_text_from_file(filepath)
        self.sql_script_execute(sql_script)

    def sql_script_execute(self, sql_script):
        # Execute SQL Script passed
        # Used for inserts, ETL and Deletes.
        try:
            sql_connection = pyodbc.connect(self.connection_string) # Define Connection
            cursor = sql_connection.cursor() # Open a Connection
            cursor.execute(str(sql_script)) # Send Sql to Server
            cursor.execute("COMMIT") # Sent Commit command
            self.log.debug('Query Result: ' + str(cursor.description))
            cursor.close()
            del cursor
            sql_connection.close()
            return True
        except Exception as e:
            self.log.error('Database Processing Failed: ' + str(e))
            return False

           # Add single file
    def add_file(self, filename):
        if os.path.isfile(filename):
            self.log.debug('File Found: ' + filename)
            self.files.append(filename)
            return True
        else: 
            self.log.error('File Not Found: ' + filename)
            return False 
    
    # Collect Files from Folder
    def collect_files_from_folder(self, path):
        counter = 0
        if os.path.isdir(path):
            for sql_file in os.listdir(path):
                if sql_file.endswith(".sql"):
                    self.add_file(os.path.join(path,sql_file))
                    counter += 1
        self.log.info(str(counter) + ' SQL Files Found in ' + path)
        return counter

    def had_errors(self):
        if self.error_count > 0:
            return True
        else:
            return False

    def longestCommonPrefix(self, strList):
        res = ''.join(c[0] for c in takewhile(lambda x:
        all(x[0] == y for y in x), zip(*strList)))   
        
        return res

    def run(self):

        start_time = time.time() # for timing the script
        self.log.info('Files to Process: ' + str(len(self.files)))
        #self.log.info(print(self.files))
        #self.log.info('Longest Prefix: ' + self.longestCommonPrefix(list(self.files[0])))

        for file in self.files:
            if os.path.isfile(file):

                # self.log.info('Processing File: ' + file)
                file_start_time = time.time() # for timing the script

                self.log.info(file + ' - Started - ')
                
                if(self.sql_script_execute(self.get_text_from_file(file))==False):

                    self.log.info(file + ' - Finished - ' + str(round(time.time() - file_start_time,3)))

            # TODO: Python Files

            # TODO: Batch Files

        self.log.info('Main Complete: ' + str(datetime.timedelta(seconds=round(time.time() - start_time,3))))

