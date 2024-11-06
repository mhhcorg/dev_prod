import os
import re
import sys
import time
from datetime import datetime
from os.path import expanduser

import env_test
from custom_logger import StandardLogging
from custom_status import Status
from folder_processor import FolderProcessor
from sql_get import SqlGet
from sql_process import SqlProcess


'''
    Folder Action Item Parser

    This will cycle through folders finding out which contains scripts and begin to execute them in order logging the data centrally.
    2020-04-30 - Finalized as a production candidate.  Repaired the looping issues. And configure imported argument.
    2020-10-01 Adding debugging log
'''

debug = True # Turns on local profile logging
log_number = 0

def user_profile_debug_log(message):
    if debug: 
        # Log Number labels the line as the sequence of logs for this run
        global log_number
        log_number += 1
        f = open(os.path.join(expanduser("~"), "python_debug.log"), "a")
        if log_number == 1:
            f.write('--------------------------------------------------------------------\n')
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + str(log_number) + ' ' + message + "\n")
        f.close()

# Debug Data Passed In
user_profile_debug_log('Started Python Manager Main Py')
user_profile_debug_log('Arguments: ' + str(sys.argv))
user_profile_debug_log('Arguments: ' + str(len(sys.argv)))

# Get Arguments as Dictionary
arg_names = ['command','content_path','methods','base_path','wait_flag']
arg_defaults = ['','','All','0','']

for i in range(len(sys.argv)):
    arg_defaults[i] = sys.argv[i]

args = dict(zip(arg_names, arg_defaults))

user_profile_debug_log('Content Path: ' + args['content_path'])


if os.path.isdir(args['content_path'] + '\\') != True or args['content_path']=='':
    args['content_path'] = os.path.dirname(args['command'])

if os.path.isdir(args['base_path'] + '\\') != True or args['base_path']=='':
    args['base_path'] = os.path.dirname(args['command'])

user_profile_debug_log('Arguments: ' + str(args))

pathname = os.path.dirname(args['content_path'])
log = StandardLogging().set_level_info().get_run_logger(args['base_path'])
log.info('Base Path: ' + args['base_path'])
log.info('Content Path: ' + args['content_path'])
log.info('Methods: ' + args['methods'])

#status = Status().setup_ini(args['base_path'])
#status.set_logger(log)
folder_processing = FolderProcessor()
folder_processing.set_folder_path(args['content_path'])
folder_processing.set_logger(log)
execution_paths = folder_processing.run()

content_paths = folder_processing.get_paths()
content_actions = folder_processing.get_actions()

# Process Each Found Folder
start_time = time.time() # for timing the script

for i in range(len(content_paths)):
    #log.info(execution_paths[i])
    #status.set('execution.plan.' + str(i),execution_paths[i])
    print(content_paths[i].replace(':','').replace(' ',''))

    if content_actions[i] =='get' and (args['methods']=='All' or args['methods']=='Get'):
        get = SqlGet()
        get.set_logger(log)
        get.set_connection_string('mssql+pyodbc://MHKM/dw_import?driver=SQL+Server')
        get.set_output_path(os.path.join(args['base_path'],'output'))
        get.collect_files_from_folder(content_paths[i])
        get.run()
        #status.set(content_paths[i].replace(':','').replace(' ','') + '.had_errors' ,str(get.had_errors()))
        
    if content_actions[i] =='process' and (args['methods']=='All' or args['methods']=='Process'):
        process = SqlProcess()
        process.set_logger(log)
        process.set_connection_string('DRIVER={SQL Server};SERVER=MHKM;DATABASE=dw_staging;Trusted_Connection=yes;')
        process.collect_files_from_folder(content_paths[i])
        process.run()
        #status.set(content_paths[i].replace(':','').replace(' ','')  + '.had_errors' ,str(process.had_errors()))
    
log.info('Batch Done: ' + str(round(time.time() - start_time,3)))
user_profile_debug_log('Batch Done: ' + str(round(time.time() - start_time,3)))