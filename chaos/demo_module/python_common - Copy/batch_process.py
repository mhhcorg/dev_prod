"""
Batch File Folder FIXME: DRAFT

Take all batch files in the process folder and execute in name order.

2020-10-01
"""

import os
import sys
import time
import datetime
import logging
import subprocess


class BatchProcess():

    def __init__(self, level='INFO'):
        self.log = ''
        self.line_format = logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(module)s] [%(funcName)s] %(message)s")
        self.log = logging.getLogger('__name__')
        self.log.setLevel(level)      
        self.error_count = 0
        self.files = []
        self.start_time = time.time() # for timing the script

    # SET LOGGER
    def set_logger(self, new_logger, level='INFO'):
        self.log = new_logger
        self.log.setLevel(level)
    
    def batch_script_execute(self, file_path):
        if os.path.isfile(file_path):
            try:
                p = subprocess.Popen(file_path, shell=True, stdout = subprocess.PIPE, cwd=rs.path.abspath("file_path"))
                stdout, stderr = p.communicate()

                if p.returncode == 0:
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
            for filename in os.listdir(path):
                if filename.endswith(".bat"):
                    self.add_file(os.path.join(path,filename))
                    counter += 1
        self.log.info(str(counter) + ' Batch Files Found in ' + path)
        return counter

    def had_errors(self):
        if self.error_count > 0:
            return True
        else:
            return False

    def run(self):

        start_time = time.time() # for timing the script
        self.log.info('Files to Process: ' + str(len(self.files)))

        for file in self.files:
            if os.path.isfile(file):

                self.log.info('Processing File: ' + file)
                file_start_time = time.time() # for timing the script

                self.log.info(file + ' - Started - ')
                
                if(self.batch_script_execute(file):

                    self.log.info(file + ' - Finished - ' + str(round(time.time() - file_start_time,3)))

        self.log.info('Main Complete: ' + str(round(time.time() - start_time,3)))

