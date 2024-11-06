""" PUT.PY - Health First Gaps in Care

    Take files within a folder and put them into a table on the database server.
    Config file for each folder defines the process of importing and destination tables.

    TODO: make it more flexible to automatically adjust columns to fit the data type found.
    TODO: Make checks for new columns and defaulting all columns to text

    2019-07-08 - File hash checking and validation
    2019-07-09 - Comments and finishing up.
    2019-07-11 - Revised to include many puts from config file.
    2019-08-18 - Adjusted to work in sub folder called app and handle CSV Files
    2019-08-22 - Adjusted to pull any table name and default
    2019-08-30 Repaired temp file issues for excel
"""
import pandas as pd
import os, sys
import csv, ast
import pyodbc
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR
import configparser
import time
import datetime
import logging
import win32com.client
import hashlib
import re
from shutil import copyfile

# VARIABLES #--------------------------------------------------------------
app_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),'..')
start_time = time.time() # for timing the script

# IMPORT CONFIG FILE
config = configparser.ConfigParser()
config.read(os.path.join(app_path,'config.ini'))

# VARIABLES
SCRIPTFILE = 'put.py' #TODO: fix this to be dynamic
sql_connection = sa.create_engine(config['PUT']['CONNECTION_STRING'])

# SETTINGS - LOG
logger = logging.getLogger()
handler = logging.FileHandler(os.path.join(app_path,config['GLOBAL']['log_folder'],SCRIPTFILE + '.log'))
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# FUNCTIONS #--------------------------------------------------------------

# GET FILE HASH
# 2019-07-09
def get_file_hash(filepath):

    BUFFER_SIZE = 65536 # Read 64K chunks
    hash = hashlib.sha1()

    with open(filepath, 'rb') as file:
        while True:
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            hash.update(data)

    return hash.hexdigest()

def get_file_record_by_hash(file_hash):
    sql_script = "SELECT * FROM files WHERE is_processed = 1 AND file_hash = ?"
    df = pd.read_sql(sql = sql_script,con = sql_connection, params = [file_hash])
    return df

# IS PROCESSED
# 2019-07-09
def is_processed(file_hash):
    df = get_file_record_by_hash(file_hash)

    if(len(df)>=1):
        logger.debug('Hash Found: ' + file_hash)
        return True
    else:
        logger.debug('Hash Not Found: ' + file_hash)
        return False

# GET FILE RECORD BY NAME
# 2019-07-09
def get_file_record_by_name(filename):
    sql_script = "select * from files where filename = ?"
    df = pd.read_sql(sql = sql_script,con = sql_connection, params = [filename])
    return df

# PUT FILE RECORD
# Saves a filename and hash to files table.  This means the file is processed.
# 2019-07-09
def put_file_record(filename,file_hash,records = 0,etl_process = 'etl'):
    df = pd.DataFrame({'process_name': [etl_process],'filename': [filename],'file_hash': [file_hash], 'is_processed': [1]})
    df.to_sql('files',con=sql_connection, if_exists='append', index=None)
    # TODO: add error checking for connection issue.

#TODO: Finished this to update processed or not.
def update_file_to_processed(file_hash):
    pass

# REMOVE PASSWORD XLSX
# Remove the password from excel and saves an unencrypted copy
def Remove_password_xlsx(filename, password_string):
    excel = win32com.client.Dispatch("Excel.Application")
    workbook = excel.Workbooks.Open(os.path.join(app_path,"put",filename), False, False, None, password_string)
    excel.DisplayAlerts = False
    workbook.SaveAs(os.path.join(app_path,"put_decrypted",filename), None, '', '')
    excel.Quit()
    logger.info('File Decrypted')

# TODO: complete this function. This needs to be dynamic from config.
def decrypt_files_if_needed(filename):
    # Decrypt File if Needed
    if (config['PUT']['ENCRYPTION_STATUS'] == 'true'):
        try:
            Remove_password_xlsx(filename,'MhhC2019')
        except:
            pass

        try:
            Remove_password_xlsx(filename,'MhhC2018')
        except:
            pass

    # TODO: return the path to the file if it is encrypted or not.

def xls_to_csv(filename, sheet, row_header = 0):

    # Check for Source Folder
    if config['PUT']['is_encrypted'] == 'true':
        df = pd.read_excel(os.path.join(app_path,"temp","put_decrypted",filename), sheet_name=sheet, header = row_header, dtype=object)
    else:
        df = pd.read_excel(os.path.join(app_path,"put",filename), sheet_name=sheet, header = row_header, dtype=object)

    df = df.dropna(how='all',axis=0)
    df['filename']  = filename
    df['sheet'] = sheet
    df['row'] = df.index + 1
    df['rowhash'] = '' # TODO: Calculate the MD5 Hash

    # Repair Column Names
    df.columns = [re.sub(r'\n', ' ', c) for c in df.columns]
    df.columns = [re.sub(r'  ', ' ', c) for c in df.columns]
    df.columns = [re.sub(r'  ', ' ', c) for c in df.columns]

    #logger.debug(df.head())

    df.to_csv(os.path.join(app_path,"temp","put_csv",filename) + '.' + sheet + '.csv', index=False)


    hash = get_file_hash(os.path.join(app_path,"temp","put_csv",filename) + '.' + sheet + '.csv')
    logger.info('Converted to CSV - Records: ' + str(df['row'].count()) + ' hash: ' + hash)

    return df['row'].count()

# TODO: Make this generic and return the DF
def headerfiller(df):
    df.columns = [re.sub(r' \n', '_', c) for c in df.columns]

# DELETE FILES
# 2019-07-09 - Not tested
def delete_files(path,pattern,maxdepth=1):
    cpath = path.count(os.sep)
    for r,d,f in os.walk(path):
        if r.count(os.sep) - cpath < maxdepth:
            for files in f:
                if files.endswith(pattern):
                    try:
                        print ("Removing " + (os.path.join(r,files)))
                        logger.debug('Removing ' + (os.path.join(r,files)))
                        #os.remove(os.path.join(r,files))
                    except Exception as e:
                        print(e)
                        logger.info(e)
                    else:
                        print ("Removed" + (os.path.join(r,files)))
                        logger.debug("Removed" + (os.path.join(r,files)))

# Puts data frame into server
# 2019-07-09
def df_to_db(self, frame, name, if_exists='fail', index=False,index_label=None, schema=None, chunksize=None, dtype=None, **kwargs):
    #logger.debug(frame.head())

    if dtype is not None:
        from sqlalchemy.types import to_instance, TypeEngine
        for col, my_type in dtype.items():
            if not isinstance(to_instance(my_type), TypeEngine):
                raise ValueError('The type of %s is not a SQLAlchemy '
                                 'type ' % col)
    table = pd.io.sql.SQLTable(name, self, frame=frame, index=index, if_exists=if_exists, index_label=index_label, schema=schema, dtype=dtype, **kwargs)

    # , dtype={col_name: NVARCHAR for col_name in df}
    table.create()
    try:
        table.insert(chunksize)
    except Exception as error:
        logger.error('DF_TO_DB Failed on Table Insert.')
        logger.exception(error)



# CSV to DB
#
# Copy CSV to database.
def csv_to_db(filename,destination_table):

    # CSV to SQL Server
    pandas_sql = pd.io.sql.pandasSQL_builder(sql_connection, schema=None)
    file_hash = get_file_hash(os.path.join(app_path,"temp","put_csv",filename))

    # Check if we should see if the file has been processed
    if config['PUT']['check_if_processed_already'] == 'true':
        # Run the check and exit if processed
        if (is_processed(file_hash) == True):
            logger.debug('File Hash for CSV Found. Skipping')
            return

    # File Not Processed or not checked

    # Get 5 Rows from the file.
    chunks = pd.read_csv(os.path.join(app_path,"temp","put_csv",filename), dtype=object, chunksize=5)

    try:
        for df in chunks:
            #logger.debug(df.head())
            df_to_db(pandas_sql, df, destination_table,index=False, if_exists='append')
        logger.info('Inserted into ' + destination_table)
    except Exception as e:
        logger.error(df.head())
        logger.error(e)

    # Save file record so it is skipped next time.
    if config['PUT']['log_file_is_processed'] == 'true':
        put_file_record(filename,file_hash,len(df),config['GLOBAL']['NAME'])
        logger.debug('File has been saved for future checking.')

# GET CONFIG SECTIONS
# Get list of all sections with the PUT prefix.
def get_config_sections():
    for section in config.sections():
        if(section.lower().find('put') != -1):
            print(section)
            put_config = config._sections[section]
            print(put_config)
            print(type(put_config))

            for key, value in put_config.items():
                print('Key:' + key + ' value:' + value)

# CREATE REQUIRED FOLDERS
# [2019-08-18 | 01:16PM | David Colon]
def create_required_folders():
    if not os.path.exists(os.path.join(app_path,'put')):
        os.makedirs(os.path.join(app_path,'put'))
    if not os.path.exists(os.path.join(app_path,'logs')):
        os.makedirs(os.path.join(app_path,'logs'))
    if not os.path.exists(os.path.join(app_path,'temp')):
        os.makedirs(os.path.join(app_path,'temp'))
    if not os.path.exists(os.path.join(app_path,'temp','put_csv')):
        os.makedirs(os.path.join(app_path,'temp','put_csv'))
    if not os.path.exists(os.path.join(app_path,'temp','put_decrypted')):
        os.makedirs(os.path.join(app_path,'temp','put_decrypted'))

# MAIN #--------------------------------------------------------------
def main():

    # Empty Log File
    open(os.path.join(app_path,config['GLOBAL']['log_folder'],SCRIPTFILE + '.log'), 'w').close()

    name = config['GLOBAL']['NAME']

    logger.info('-- Main Started -- ' + name.upper())

    #Create Folders Needed for this script
    create_required_folders()

    #Loop through multiple put sections
    for section in config.sections():
        if(section.lower().find('put') != -1):
            logger.info('Put Section Started: ' + section)

            file_filter = config[section]['FILE_FILTER']

            for filename in os.listdir(os.path.join(app_path,"put")):

                # Filter only for Excel Files
                if (filename.endswith(".xlt") == True) or (filename.endswith(".xlsx") == True) or (filename.endswith(".xls") == True) or (filename.endswith(".csv") == True):
                    # Filter only for files matching the file filter
                    if (len(file_filter) > 0):
                        logger.debug(filename.lower())
                        logger.debug('Result: ' + str(filename.lower().find(file_filter.lower())))
                        if (filename.lower().find(file_filter.lower()) == -1):
                            logger.debug('File Skipped: ' + filename)
                            continue

                    logger.info('File Started: ' + filename)
                    #file_start_time = time.time() # for timing the script

                    file_hash = get_file_hash(os.path.join(app_path,"put",filename))

                    # Get the destination table name
                    # 2019-08-22
                    if len(config[section]['DESTINATION_TABLE']) == 0:
                        # Get the file without the file extension.
                        destination_table = os.path.splitext(filename)[0]
                    else:
                        destination_table = config[section]['DESTINATION_TABLE']

                    logger.debug('Destinatoin Table: ' + destination_table)

                    # FIXME: Uncomment for production
                    if config[section]['check_if_processed_already'] == 'true':
                        if is_processed(file_hash) == True:
                            logger.info('File Already Processed. Skipping')
                            continue
                        else:
                            logger.info('File Not Found.')

                    # IF EXCEL
                    if (filename.endswith(".xlt") == True) or (filename.endswith(".xlsx") == True) or (filename.endswith(".xls") == True):
                        # Excel File
                        # TODO: Handle the encrypted vs non-encrypted
                        excel_file = pd.ExcelFile(os.path.join(app_path,"put",filename))

                        # Get names of sheets
                        logger.debug('Found Sheets: ' + str(excel_file.sheet_names))

                        sheet_filter = config[section]['SHEET']
                        sheet_line_start = int(config[section]['SHEET_LINE_START'])


                        logger.debug('Sheet Filter: ' + sheet_filter)

                        #records = 0
                        # Handle Each sheet name seperately
                        for sheet_name in excel_file.sheet_names:
                            if(sheet_name.lower().find(sheet_filter.lower())  != -1):
                                logger.info('Worksheet Started: ' + sheet_name)
                                records = xls_to_csv(filename,sheet_name,sheet_line_start)
                                csv_to_db(filename + '.' + sheet_name + '.csv', destination_table)
                            else:
                                logger.debug('Worksheet Skipped: ' + sheet_name)
                    else:
                        # CSV FILE
                        csv_to_db(os.path.join(app_path,"put",filename), destination_table)


                    # Backup the
                    # TODO: compare the source data with the put folder and if they are different, then import to the put folder. This is for when the files are not in the put folder but somewhere else.
                    #copyfile(os.path.join(app_path,"put",filename), os.path.join(app_path,"put_backup",filename))

                    # Save File
                    # FIXME: Unblock in production
                    #put_file_record(filename,file_hash, records, config['GLOBAL']['NAME'])
                    #put_file_record(filename,file_hash)
                    #logger.info('Saved as Processed File')

    config['STATUS']['LAST_RUN'] = str(datetime.datetime.now())
    config['STATUS']['RESULT'] = 'Successful'
    config['PUT']['REPROCESS_FILES'] = 'false'

    # Save Config File
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
        logger.info('Config File Written')

    # Delete resulting temp files.
    # TODO: Create delete function
    #delete_files(os.path.join(app_path,"put_decrypted"),'.xlsx')
    #delete_files(os.path.join(app_path,"put_decrypted"),'.xls')
    #delete_files(os.path.join(app_path,"put_decrypted"),'.xlk')
    #delete_files(os.path.join(app_path,"put_csv"),'.csv')

    logger.info('Completed')

# MAIN
main()