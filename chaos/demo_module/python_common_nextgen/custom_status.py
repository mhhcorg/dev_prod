import os
import sys
import pathlib

from datetime import datetime

import configparser
import io
import logging
from filelock import Timeout, FileLock

class Status:
    """
    STATUS

    VERSION: 1.0
    CREATED: 2019-01-25
    AUTHOR: david@colon.me

    2020-03-23 - Added the unset INI function
    2020-04-30 - Moved class to instance variables.

    """
    # v1.2020-01-26

    # Options: json file, sql table,
    def __init__(self, method='ini'):

        # Status Tracking Method
        self.filepath = ''   # full path of the file name
        self.filehandle = ''  # direct path to the file handle
        # 1 if ready to save, 0 if the file or connection needs to be opened.
        self.is_ready = 0

        # Logging TODO: Clean up with logging import. Or changable with passed variable. Learn how to log from sub classes to the parent operation.
        self.log = logging.getLogger('__main__')
        self.log.debug('Class Initiated')

        self.method = method

    def setup_ini(self, folder, filename = 'status.ini'):
        if self.method=='ini':
            self.set_file_path(folder, filename)

            # Create file if it doesn't Exist
            if os.path.exists(self.filepath) == False:
                f = open(self.filepath, "w")
                f.close

        else:
            print('DANGER')
        
        return self

    def set_file_path(self, new_file_path, filename):

        self.filepath = os.path.join(new_file_path,filename)

        self.log.debug(self.filepath)

        # Create the path and file
        # Check if file exists and the path is actually a file and not a directory.
        # if not exists create the file.
        path = pathlib.Path(self.filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
    
        self.is_ready = 1
        return True
    
    def set_logger(self, logger):
        self.log = logger

    def set(self, key, value):
        if self.method == 'ini':
            self._set_ini(key,value)
        else:
            self.log.debug('Missing Method... So nothing tod o')
    
    def unset(self, key):
        if self.method == 'ini':
            self._unset_ini(key)
        else:
            self.log.debug('Missing Method... So nothing tod o')


    def get(self, key, default=''):
        if self.method == 'ini':
            result = self._get_ini(key,default)
        else:
            self.log.debug('Missing Method... So nothing tod o')
            result = ''
        
        return result
        # Look for and get the result or return the default
    
    def get_modified_at(self, key):
        if self.method == 'ini':
            result = self._get_modified_at(key)
        else:
            self.log.debug('Missing Method... So nothing tod o')
            result = ''

        return result

    def _unset_ini(self, key):
        # Load the configuration file

        # Set false and exit if not ok to run.
        # Maybe missing path or not access etc.
        if self.is_ready == 0:
            return False

        # Create the lock to modify the file.  See if another app is using the file and wait.
        # https://pypi.org/project/filelock/
        
        lockfile = self.filepath + r'.lock'

        self.log.debug(lockfile)
        lock = FileLock(lockfile, timeout=1)

        # Lock Until finished with process
        with lock:

            config = configparser.RawConfigParser()

            config.read(self.filepath)

            if config.has_section('STATUS') == False:
                config.add_section('STATUS')

            config.remove_option('STATUS', key.lower())

            if config.has_section(str(key).upper()) == True:
                config.remove_section(str(key).upper())
        
            config.write(open(self.filepath,"w"))
        
        return True

    def _set_ini(self, key, value):
        # Load the configuration file

        # Set false and exit if not ok to run.
        # Maybe missing path or not access etc.
        if self.is_ready == 0:
            return False

        # Create the lock to modify the file.  See if another app is using the file and wait.
        # https://pypi.org/project/filelock/
        
        lockfile = self.filepath + r'.lock'

        self.log.debug(lockfile)
        lock = FileLock(lockfile, timeout=1)

        # Lock Until finished with process
        with lock:

            config = configparser.RawConfigParser()

            config.read(self.filepath)

            if config.has_section('STATUS') == False:
                config.add_section('STATUS')

            config.set('STATUS', key.lower(), value)

            if config.has_section(str(key).upper()) == False:
                config.add_section(str(key).upper())

            # Update the file the last modified date
            #config.set('INFO', 'modified_at', datetime.now().strftime("%Y-%m/%d %H:%M:%S"))
            config.set(str(key).upper(), 'modified_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Counts
            if config.has_option(str(key).upper(), 'update_count') == False:
                config.set(str(key).upper(), 'update_count', 1)
            else:
                config.set(str(key).upper(), 'update_count', int(config.get(str(key).upper(), 'update_count')) + 1)

            config.write(open(self.filepath,"w"))
        
        return True
    
    def _get_ini(self, key, default):

        config = configparser.RawConfigParser()
        config.read(self.filepath)
        try:
            result = config.get('STATUS', key.lower())
        except:
            result = default
        
        return result

    def _get_modified_at(self, key):
        config = configparser.RawConfigParser()
        config.read(self.filepath)

        try:
            result = config.get(key.upper(),'modified_at')
        except:
            result = ''
        
        return result

    def get_all(self):
        if self.method == 'ini':
            result = self.get_all_ini()
        else:
            self.log.debug('Missing Method... So nothing tod o')
            result = ''

        return result

    def get_all_ini(self):

        message =  ''

        config = configparser.RawConfigParser()
        config.read(self.filepath)

        for i in sorted(list(config.items('STATUS'))):
            message = message + i[0] + ' = ' + i[1] + ' @ ' + config.get(str(i[0]).upper(),'modified_at') + ' x' + config.get(str(i[0]).upper(),'update_count') + '\n'
        
        return message
        





