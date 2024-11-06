"""
Process Change Detection Queries

Runs a specific query with output if ID and RECORD and save a copy. Then each run it compared the results to the saved copy reporting changes and additions.

2019-10-21 Created first draft working. 
"""

import os, sys
import pandas as pd
import csv, ast
import pyodbc
import sqlalchemy as sa
from sqlalchemy import create_engine
import time
from datetime import datetime
import logging
import configparser
from shutil import copyfile # For file moves

# VARIABLES
SCRIPTFILE='detect_change.py'

# SETTINGS
app_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),'..')
start_time = time.time() # for timing the script

# IMPORT CONFIG FILE
config = configparser.ConfigParser()
config.read(os.path.join(app_path,'config.ini'))

# SETTINGS - LOG
logger = logging.getLogger()
handler = logging.FileHandler(os.path.join(app_path,config['GLOBAL']['log_folder'],SCRIPTFILE + '.log'))
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


## FUNCTIONS ####

def get_sql_from_file(filename):
    fd = open(os.path.join(app_path,r"detect_change",filename),'r')
    sql_file = fd.read()
    fd.close
    return sql_file

# SAVE MESSAGE
# Saves a message to the file server path.
# Defaults to Messages folder in local user documents
# 2019-10-22
def save_message(message,path='',tag=''):
    if path=='':
        path = os.getenv("USERPROFILE") + "\\documents\\messages\\" + file_date_stamp +  "_" + SCRIPTFILE + tag + ".txt"
    
    # Creat Folder if Needed
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Save the message and close
    with open(path, 'w') as file:
        file.write('Timestamp: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")  + '\n')
        file.write('App:       ' + app_path + '\n')
        file.write('File:      ' + SCRIPTFILE + '\n\n')
        file.write('Message:   ' + message)
        file.close() 


# MAIN
def main():
    # Empty Log File
    open(os.path.join(app_path,config['GLOBAL']['log_folder'],SCRIPTFILE + '.log'), 'w').close()

    logging.info('-- Main Started --')
    logging.info(sys.argv[0])
    logging.info('App Path: ' + app_path)

    # For tagging files with the same timestamp
    file_date_stamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Start Connection
    try:
        sql_connection = sa.create_engine(config['GET']['connection_string'])
    except Exception as e:
        logging.error('Database connection failed.' + str(e))
        sys.exit("Connection Failed")

    # Rotate through all SQL Files in Folder
    for sql_file in os.listdir(os.path.join(app_path,"detect_change")):
        # Get Only SQL Files
        if sql_file.endswith(".sql"):
            filename, file_extention = os.path.splitext(sql_file)
            logging.info(filename + file_extention + ' - Started - ')

            file_start_time = time.time() # for timing the script

            sql_statement = get_sql_from_file(sql_file)

            # Get Database DF
            try:
                df = pd.read_sql(sql = sql_statement,con = sql_connection, index_col='id')
            except Exception as e:
                logging.error('Query Failed.' + str(e))
                continue # Jump to next file

            base_file = os.path.join(app_path,'detect_change','data',filename + '.csv')
            archive_file = os.path.join(app_path,'detect_change','data',filename + '_' + file_date_stamp + '.csv')
        
            logging.info('Records Returned: ' + str(len(df)))

            # Check if File Exists
            if os.path.isfile(base_file):

                # Get the Base file since it exists
                df_base = pd.read_csv(base_file, index_col='id', delimiter=',')
                logging.info('File Exists, comparing.')

                # Join Base to Test
                df_combined = df.join(df_base, lsuffix='_test', rsuffix='_base', how='left')

                # Save Differences
                df_differences = df_combined[df_combined['record_base'] != df_combined['record_test']]
            
                if len(df_differences) > 0:
                    df_differences.to_csv(os.path.join(app_path,'detect_change','results',filename + '_differences_' + file_date_stamp + '.csv'))
                    logging.info('Differences Found: ' + str(len(df_differences)))
                else:
                    logging.info('No Differences Found.')

                # Save New Records
                df_new = df_combined[df_combined['record_test'].isnull()]

                if len(df_new) > 0:
                    df_new.to_csv(os.path.join(app_path,'detect_change','results',filename + '_new_' + file_date_stamp + '.csv'))
                    logging.info('New Records Found: ' + str(len(df_new)))
                else:
                    logging.info('No New Records Found.')

                # If Changes Detected Prepare for next backup.
                if len(df_differences) > 0 or len(df_new) > 0:
                    # Archive and Date the File
                    copyfile(base_file, archive_file)
                    df.to_csv(base_file,index = True, header=True)
            else:
                df.to_csv(base_file,index = True, header=True)
                logging.info('File Does not exist. saving.')

            logging.info(filename + ' - Finished - ' + str(round(time.time() - file_start_time,3)))
    logging.info('Main Complete: ' + str(round(time.time() - start_time,3)))

main()