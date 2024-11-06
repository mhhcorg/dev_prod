"""
Process SQL Folder to CSV

Takes all SQL files within the PROCESS subfolder and saves the output as CSV to an OUTPUT FOLDER.

CREATED:    2019-03-18
MODIFIED:   2019-08-18
2019-06-20 Added logging
2019-06-21 Fixed time tracking and continue on error.
2019-07-16 added write to excel
2019-08-18 Made available to work in the APP sub folder
2019-10-20 Added the option to copy to published folder.
2020-03-21 Converted Class
2023-03-17 Updated to accept a separator adjustment
2023-05-24 Updated to use pipe. FIXME: This isn't working as a parameter.
"""

import os, sys
import pandas as pd
import csv, ast
import pyodbc
""" import sqlalchemy as sa
from sqlalchemy import create_engine """
import time
import datetime
import logging
from shutil import copyfile # For file moves

class SqlGet():

    def __init__(self, level='DEBUG'):
        self.line_format = logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(module)s] [%(funcName)s] %(message)s")
        self.log = logging.getLogger('__name__')
        self.log.setLevel(level)
        self._files = []
        self.error_count = 0
        self.output_file_type = 'txt'
        self.start_time = time.time() # for timing the script
        self.connection_string = ''
        self.output_path = ''
        self.publish_path = ''
        self.backup_path = ''
        self.backup_age = 0
        self.separator = ','
        
    # SET LOGGER
    def set_logger(self, new_logger, level='DEBUG'):
        self.log = new_logger
        self.log.setLevel(level)
    
    # SET CONNECTION STRING
    def set_connection_string(self, new_connection_string):
        self.connection_string = new_connection_string

    # SET OUTPUT PATH
    def set_output_path(self, new_path):
        self.output_path = new_path
        if os.path.isdir(new_path) == False:
            self.log.warn('Output Path doesn\'t exist. It will be created: ' + new_path)

    # SET OUTPUT PATH
    def set_publish_path(self, new_path):
        self.publish_path = new_path
        if os.path.isdir(self.publish_path) == False:
            self.log.warn('Publish Path doesn\'t exist. It will be created: ' + new_path)            

    # SET OUTPUT PATH
    def set_backup_path(self, new_path):
        self.backup_path = new_path
        if os.path.isdir(self.backup_path) == False:
            self.log.warn('Backup Path doesn\'t exist. It will be created: ' + new_path)

    def set_separator(self, separator):
        if separator in [',','|','||','","']:
            self.separator = separator
            self.log.info('Separator Set to:' + separator)
        else:
            self.log.info('Invalid Separator attempted, defaulted back to comma')
            self.separator = ','

    # Add single file
    def add_file(self, filename):
        if os.path.isfile(filename):
            self.log.debug('File Found: ' + filename)
            self._files.append(filename)
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

    
    def run(self):

        if len(self.output_path) == 0:
            self.log.error('No Output Path Defined. Stopping.')
            self.error_count+=1
            return False

        if len(self.connection_string) == 0:
            self.log.error('No Connection Path Defined. Stopping.')
            self.error_count+=1
            return False
        
        self.log.info('SQL Get DEV') 
        self.log.info('Connection String: {}'.format(self.connection_string)) 

        start_time = time.time() # for timing the script
        self.log.info('Files to Process: ' + str(len(self._files)))
        #sql_connection = sa.create_engine(self.connection_string)

        sql_connection = pyodbc.connect(self.connection_string)

        run_date_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H%M%S')
        
        #self.log.info('Test:' + str(len(self.publish_path)))

        # if Published path defined created if needed
        if len(self.publish_path) > 0:
            if not os.path.exists(self.publish_path):
                os.makedirs(self.publish_path)
                self.log.info('Publish Path Created')

        # If Backups defined create the backup folder
        if len(self.backup_path) > 0: 
            os.makedirs(os.path.join(self.backup_path,run_date_time))
            self.log.info('Backup Path Created')

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        for file in self._files:
            if os.path.isfile(file):
                #self.log.info('Processing File: ' + file)
                file_start_time = time.time() # for timing the script

                # Get SQL From File
                try: 
                    fd = open(file,'rt')
                    query = fd.read()
                    fd.close
                except Exception as e:
                    self.log.error(file + str(e))
                    self.error_count+=1
                else:
                    # Prepare Destination File Path.
                    destination_file_base, ext = os.path.splitext(os.path.basename(file))
                    destination = os.path.join(self.output_path,destination_file_base + '.' + self.output_file_type)
                    self.log.debug(ext)
                    # Try to connect to DB and get the data to a Pandas Data Frame
                    try:
                        cursor = sql_connection.cursor()
                        cursor.execute(query)
                        data = []
                        columns = []

                        while True:
                            try:
                                result = cursor.fetchall()
                                #if len(result) > 0:
                                data = []
                                columns = [columns[0] for columns in cursor.description]
                                data.extend(dict(zip(columns, row)) for row in result)

                            except pyodbc.ProgrammingError as e:
                                if "No results.  Previous SQL was not a query." in str(e):
                                    pass
                                else:
                                    raise e 
                            if not cursor.nextset():
                                break

                        if len(data) > 0:
                            df = pd.DataFrame(data)
                        else:
                            df = pd.DataFrame(columns=columns)

                        cursor.close()

                    except Exception as e:
                        self.log.error('Query Connection / Query Failed: ' + str(e))
                        #df.empty
                        self.error_count+=1

                    else: 
                        self.log.debug('Records Returned: ' + str(len(df)))

                        # Try to save df to file.
                        try: 
                            self.log.debug('Saving Data: ' + destination)
                            self.log.debug('Separator: ' + self.separator)
                            df.to_csv(destination, index = None, header=True,sep=self.separator)
                            df.empty

                        except Exception as e:
                            self.log.error('Saving File Failed: ' + str(e))
                            df.empty
                            self.error_count+=1
                        else:
                            self.log.info('[' + file + '] Done: ' + str(round(time.time() - file_start_time,3)) + 's for ' + str(len(df)) + ' Records.')

                            # Publish and Backup
                            if len(self.publish_path) > 0:
                                copyfile(destination,os.path.join(self.publish_path,destination_file_base + '.csv'))
                            
                            if len(self.backup_path) > 0:
                                copyfile(destination,os.path.join(self.backup_path,run_date_time,destination_file_base + '.csv'))

        self.log.info('Get Process Complete: ' + str(datetime.timedelta(seconds=round(time.time() - start_time,3))))