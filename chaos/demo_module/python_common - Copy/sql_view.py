"""
    CREATE VIEWS

    Looks for SQL files in the folder and replaces the views in the staging db with the SQL.

    CREATED:    2019-06-20
    MODIFIED:   2019-06-20

"""

import os, sys
import pyodbc
import time
import logging
import sqlalchemy as sa
import pandas as pd
from sqlalchemy import create_engine

# VARIABLES
SCRIPTFILE='create_views.py'
sql_connection_string = r'DRIVER={SQL Server};SERVER=MHKM;DATABASE=dm_uds;Trusted_Connection=yes;'


# SETTINGS
app_path = os.path.dirname(os.path.realpath(sys.argv[0]))
start_time = time.time() # for timing the script

# SETTINGS - LOG
logger = logging.getLogger()
handler = logging.FileHandler(SCRIPTFILE + '.log')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def get_text_from_file(filename):
    # Get the text from SQL File
    fd = open(os.path.join(app_path,r'views',filename),'r')
    sql_file = fd.read()
    fd.close
    return sql_file

def sql_file_execute(sql_file):
    # Get SQL Text then send to execute
    sql_script = get_text_from_file(sql_file)
    sql_script_execute(sql_script)

def sql_script_execute(sql_script):
    # Execute SQL Script passed
    # Used for inserts, ETL and Deletes.
    try:
        sql_connection = pyodbc.connect(sql_connection_string) # Define Connection
        cursor = sql_connection.cursor() # Open a Connection
        cursor.execute(sql_script) # Send Sql to Server
        cursor.execute("COMMIT") # Sent Commit command
        cursor.close()
        del cursor
        sql_connection.close()
        return True
    except Exception as e:
        logging.error('Sql Execution Failed' + str(e))
        return False

def test_sql(sql_script):
    # Get SQL Data and Save to CSV
    sql_connection_string = r'mssql+pyodbc://MHKM/dm_uds?driver=SQL+Server'

    try:
        sql_connection = sa.create_engine(sql_connection_string)
        df = pd.read_sql(sql = sql_script,con = sql_connection)
        logging.info(df.shape[0])
    except Exception as e:
        logging.error('Database connection failed.' + str(e))
        return False
    else:
        return True

def test_view(viewname):
    sql_connection_string = r'mssql+pyodbc://MHKM/dm_uds?driver=SQL+Server&trusted_connection=yes'

    logging.info('Testing: ' + viewname)
    try:
        sql_connection = sa.create_engine(sql_connection_string)
        sql_script = r'SELECT TOP 5 * from ' + viewname
        df = pd.read_sql(sql = sql_script,con = sql_connection)
        logging.info('Test Results (Max 5): ' + str(df.shape[0]))
        df.empty
    except Exception as e:
        logging.error('Failed Test:' + str(e))

def main():
    # Empty Log File
    open(SCRIPTFILE + '.log', 'w').close()

    logging.info('--- MAIN ---')
    # Look Through Files
    for filename in os.listdir(os.path.join(app_path,r'views')):
        # Get Only SQL Files
        if filename.endswith(".sql"):
            logging.info(filename + ' - Started - ')
            file_start_time=time.time()

            sql_script = r'DROP VIEW ' + (os.path.splitext(filename)[0])
            sql_script_execute(sql_script)
            logging.info(os.path.splitext(filename)[0] + ' Dropped')

            # Create view script from select query in file
            sql_script = r'CREATE VIEW ' + (os.path.splitext(filename)[0]) + ' AS ' + get_text_from_file(filename) + ';'
            if(sql_script_execute(sql_script)==False):
                logging.error('Create Failed. Continueing with next file.')
                #break # Stop looping through files.
            else:
                logging.info(os.path.splitext(filename)[0] + ' Created')
                test_view(os.path.splitext(filename)[0])
                logging.info(os.path.splitext(filename)[0] + ' - Finished - ' + str(round(time.time() - file_start_time,3)))

    logging.info('Main Complete: ' + str(round(time.time() - start_time,3)))

main()