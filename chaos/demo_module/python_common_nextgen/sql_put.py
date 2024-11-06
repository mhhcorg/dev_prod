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
    2019-08-30 - Repaired temp file issues for excel, Fixed start line issue if CSV doesn't start at 0.
    2019-12-17 - Line Number Checks. Added new line and multiple space clean up in data.
    2020-03-21 - Converted to Class
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

class SqlPut():

    # Class 
    log = ''
    error_count = 0
    files = []
    csv_files = []
    sql_connection = ''
    
    # External Configurable
    connection_string = ''
    temp_path = ''
    database_name = ''
    table_name = ''

    run_date_time = '' #used for tables and temp.

    reprocess_files = True
    check_if_processed_already = False
    test_processed_method = 'DB'
    test_processed_path = '' # dw_import.dbo.files
    put_method = 'Replace' # Replace or Append

    excel_is_encrypted = False
    excel_encryption_passwords = []
    excel_always_created_csv = True
    excel_sheet_filters = []
    start_row = 0

    def __init__(self, level='INFO'):
        self.line_format = logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(module)s] [%(funcName)s] %(message)s")
        self.log = logging.getLogger('__name__')
        self.log.setLevel(level)
        self.run_date_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
        
    # SET LOGGER
    def set_logger(self, new_logger, level='INFO'):
        self.log = new_logger
        self.log.setLevel(level)
    
    # SET CONNECTION STRING
    def set_connection_string(self, new_connection_string):
        self.connection_string = new_connection_string

    def set_table_name(self, new_table):
        self.table_name = new_table
    
    def set_temp_path(self, new_path):
        self.temp_path = new_path
    
    def add_sheet_filter(self, new_filter):
        self.excel_sheet_filters.append(new_filer)

    def get_text_from_file(self, filepath):
        # Get the text from SQL File
        fd = open(filepath)
        text = fd.read()
        fd.close
        return text

    # Add single file
    def add_file(self, filename):
        if os.path.isfile(filename):
            self.log.debug('File Found: ' + filename)
            filelist.append(filename)
            return True
        else: 
            self.log.error('File Not Found: ' + filename)
            return False 
    
    # Collect Files from Folder
    def collect_files_from_folder(self, path):
        counter = 0
        if os.path.isdir(path):
            for filepath in os.listdir(path):
                self.add_file(os.path.join(path,filepath))
                counter += 1
        self.log.info(str(counter) + ' Files Found in ' + path)
        return counter

    def had_errors(self):
        if self.error_count > 0:
            return True
        else:
            return False

    # GET FILE HASH
    # 2019-07-09
    def get_file_hash(self, filepath):

        BUFFER_SIZE = 65536 # Read 64K chunks
        hash = hashlib.sha1()

        with open(filepath, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                hash.update(data)

        return hash.hexdigest()
    

    # IS PROCESSED
    # 2019-07-09
    def is_processed(self, file_hash):
        return False
        
        """ df = get_file_record_by_hash(file_hash)

        if(len(df)>=1):
            logger.debug('Hash Found: ' + file_hash)
            return True
        else:
            logger.debug('Hash Not Found: ' + file_hash)
            return False """

    # GET FILE RECORD BY NAME
    # 2019-07-09
    def get_file_record_by_name(self, filename):
        pass
        #sql_script = "SELECT * FROM files WHERE filename = ?"
        #df = pd.read_sql(sql = sql_script,con = sql_connection, params = [filename])
        #return df

    # PUT FILE RECORD
    # Saves a filename and hash to files table.  This means the file is processed.
    # 2019-07-09
    def put_file_record(self, filename,file_hash,records = 0,etl_process = 'etl'):
        pass
        #df = pd.DataFrame({'process_name': [etl_process],'filename': [filename],'file_hash': [file_hash], 'is_processed': [1]})
        #df.to_sql('files',con=sql_connection, if_exists='append', index=None)
        # TODO: add error checking for connection issue.


    # REMOVE PASSWORD XLSX
    # Remove the password from excel and saves an unencrypted copy
    def Remove_password_xlsx(self,filepath, password_string):
        excel = win32com.client.Dispatch("Excel.Application")
        workbook = excel.Workbooks.Open(os.path.join(app_path,"put",filename), False, False, None, password_string)
        excel.DisplayAlerts = False
        workbook.SaveAs(os.path.join(app_path,"put_decrypted",filename), None, '', '')
        excel.Quit()
        self.log.info('File Decrypted')

    # TODO: complete this function. This needs to be dynamic from config.
    def decrypt_files_if_needed(self, filepath):
        # Decrypt File if Needed
        if (self.excel_is_encrypted == True):
            try:
                Remove_password_xlsx(filepath,'123')
            except:
                pass

            try:
                Remove_password_xlsx(filepath,'123')
            except:
                pass

    # TODO: return the path to the file if it is encrypted or not.

    def xls_to_df(self, filename, sheet, row_header = 0):

        # Check for Source Folder
        if self.excel_is_encrypted == True:
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

        df.replace(r'\s', '', regex = True, inplace = True)
        df.replace(r'\\s', '', regex = True, inplace = True)
        df.replace(r'  ', ' ', inplace = True)
        df.replace(r'  ', ' ', inplace = True)


        return df

    # TODO: Make this generic and return the DF
    def headerfiller(self, df):
        df.columns = [re.sub(r' \n', '_', c) for c in df.columns]

    # DELETE FILES
    # 2019-07-09 - Not tested
    def delete_files(self, path,pattern,maxdepth=1):
        cpath = path.count(os.sep)
        for r,d,f in os.walk(path):
            if r.count(os.sep) - cpath < maxdepth:
                for files in f:
                    if files.endswith(pattern):
                        try:
                            print ("Removing " + (os.path.join(r,files)))
                            self.log.debug('Removing ' + (os.path.join(r,files)))
                            #os.remove(os.path.join(r,files))
                        except Exception as e:
                            print(e)
                            self.log.info(e)
                        else:
                            print ("Removed" + (os.path.join(r,files)))
                            self.log.debug("Removed" + (os.path.join(r,files)))

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
            self.log.error('DF_TO_DB Failed on Table Insert.')
            self.log.exception(error)

    # CSV to DB
    # Copy CSV to database.
    def csv_to_db(self, filename,destination_table, start_line = 0):

        if start_line > 0:
            self.log.debug('Skipping CSV Rows: ' + str(start_line))

        # CSV to SQL Server
        pandas_sql = pd.io.sql.pandasSQL_builder(self.sql_connection, schema=None)
        #file_hash = get_file_hash(os.path.join(app_path,"temp","put_csv",filename))

        # Check if we should see if the file has been processed
        if self.check_if_processed_already == True:
            # Run the check and exit if processed
            if (self.is_processed(file_hash) == True):
                self.log.debug('File Hash for CSV Found. Skipping')
                return

        # File Not Processed or not checked

        # Get 5 Rows at a time from the CSV file.
        chunks = pd.read_csv(os.path.join(app_path,"temp","put_csv",filename), dtype=object, chunksize=5, skiprows=start_line)

        try:
            for df in chunks:
                #logger.debug(df.head())
                df_to_db(pandas_sql, df, destination_table,index=False, if_exists='append')
            self.log.debug(df.head(1))
            self.log.info('Inserted into ' + destination_table)
        except Exception as e:
            self.log.error(df.head())
            self.log.error(e)

        # Save file record so it is skipped next time.
        if config['PUT']['log_file_is_processed'] == 'true':
            self.put_file_record(filename,file_hash,len(df),config['GLOBAL']['NAME'])
            self.log.debug('File has been saved for future checking.')


    def df_to_db(self, df,destination_table):

        # SQL Server
        pandas_sql = pd.io.sql.pandasSQL_builder(self.sql_connection, schema=None)
        
        # Delete the top rows if required
        if self.start_row > 0:
            df.drop(df.index[0:self.start_row]-1)

        df = df.astype(str) # Convert to Strings

        try:
            # Do 5 records at a time
            n = 5 # Records in a chunk
            for i in range(0,df.shape[0],n):
                df_to_db(pandas_sql, df[i:i+n], destination_table, index=False, if_exists='append')

            self.log.debug(df.head(1))
            self.log.info('Inserted into ' + destination_table)
        except Exception as e:
            self.log.error(df.head())
            self.log.error(e)


    def get_file_record_by_hash(self, file_hash):
        sql_script = "SELECT * FROM files WHERE is_processed = 1 AND file_hash = ?"
        df = pd.read_sql(sql = sql_script,con = sql_connection, params = [file_hash])
        return df

    # CREATE REQUIRED FOLDERS
    # 2020-03-21
    def create_required_folders(self):

        if len(self.temp_path)>0:

            if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path)
                self.log.debug('Created Folder: ' + self.temp_path)
            if not os.path.exists(os.path.join(self.temp_path,'put_csv')):
                os.makedirs(os.path.join(self.temp_path,'put_csv'))
                self.log.debug('Created Folder: ' + os.path.join(self.temp_path,'put_csv'))
            if not os.path.exists(os.path.join(self.temp_path,'put_decrypted')):
                os.makedirs(os.path.join(self.temp_path,'put_decrypted'))
                self.log.debug('Created Folder: ' + os.path.join(self.temp_path,'put_decrypted'))
            return True
        else:
            self.log.error('Temp Folder Not Defined. Stopping')
            return False

    def run(self):

        start_time = time.time() # for timing the script

        self.log.info('Files to Process: ' + str(len(self.files)))
        
        self.create_required_folders()

        for file in self.files:
            if os.path.isfile(file):

                self.log.info('Processing File: ' + file)
                file_start_time = time.time() # for timing the script

                #file_hash = self.get_file_hash(file)
                destination_table = self.set_table_name
                sheet_line_start = int(self.start_row)

                # Test for Excel
                if (file.endswith(".xlt") == True) or (file.endswith(".xlsx") == True) or (file.endswith(".xls") == True):
                    # Excel File
                    # TODO: Handle the encrypted vs non-encrypted

                    excel_file = pd.ExcelFile(file)

                    # Get names of sheets
                    self.log.debug('Found Sheets: ' + str(excel_file.sheet_names))

                    sheets_to_process = []

                    # Get list of sheets to process which pass the filter
                    for sheet_name in excel_file.sheet_names:
                        if len(self.excel_sheet_filters) > 0:
                            for sheet_filter in self.excel_sheet_filters:
                                if(sheet_name.lower().find(sheet_filter.lower())  != -1):
                                    sheets_to_process.append(sheet_name)
                        else:
                            sheets_to_process.append(sheet_name)
                    
                    # Process Sheets which passed filter
                    for sheet in sheets_to_process:
                        df = xls_to_df(file,sheet,self.start_row)

                        #logger.debug(df.head())

                        df.to_csv(os.path.join(self.temp_path,"put_csv",filename) + '.' + sheet + '.csv', index=False)

                        hash = self.get_file_hash(os.path.join(self.temp_path,"put_csv",filename) + '.' + sheet + '.csv')
                        logger.info('Converted to CSV - Records: ' + str(df['row'].count()) + ' hash: ' + hash)
                        
                        csv_to_db(file + '.' + sheet + '.csv', destination_table)
                    else:
                        self.log.debug('Worksheet Skipped: ' + sheet)
                
                # Test for csv
                if (file.endswith(".csv") == True):
                    self.csv_to_db(file), destination_table,sheet_line_start


                # Backup the
                # TODO: compare the source data with the put folder and if they are different, then import to the put folder. This is for when the files are not in the put folder but somewhere else.
                #copyfile(os.path.join(app_path,"put",filename), os.path.join(app_path,"put_backup",filename))

                # Save File
                # FIXME: Unblock in production
                #put_file_record(filename,file_hash, records, config['GLOBAL']['NAME'])
                #put_file_record(filename,file_hash)
                #logger.info('Saved as Processed File')

                # Delete resulting temp files.
                # TODO: Create delete function
                #delete_files(os.path.join(app_path,"put_decrypted"),'.xlsx')
                #delete_files(os.path.join(app_path,"put_decrypted"),'.xls')
                #delete_files(os.path.join(app_path,"put_decrypted"),'.xlk')
                #delete_files(os.path.join(app_path,"put_csv"),'.csv')

        self.log.info('Completed')  
        self.log.info('Main Complete: ' + str(round(time.time() - start_time,3)))

