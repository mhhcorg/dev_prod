import os
import re
import sys

import env_production
from custom_logger import StandardLogging
from custom_status import Status
from folder_processor import FolderProcessor
from sql_get import SqlGet
from sql_process import SqlProcess
import time
import datetime


'''
    Folder Action Item Parser

    This will cycle through folders finding out which contains scripts and begin to execute them in order logging the data centrally.
    2020-04-30 - Finalized as a production candidate.  Repaired the looping issues. And configure imported argument.
'''


# Get Arguments as Dictionary
arg_names = ['command','content_path','methods','base_path','wait_flag']
arg_defaults = ['','','All','0','']

for i in range(len(sys.argv)):
    arg_defaults[i] = sys.argv[i]

args = dict(zip(arg_names, arg_defaults))

#print('Content Path: ' + args['content_path'])
#print(args)

if os.path.isdir(args['content_path'] + '\\') != True or args['content_path']=='':
    args['content_path'] = os.path.dirname(args['command'])

if os.path.isdir(args['base_path'] + '\\') != True or args['base_path']=='':
    args['base_path'] = os.path.dirname(args['command'])

#print(args)

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