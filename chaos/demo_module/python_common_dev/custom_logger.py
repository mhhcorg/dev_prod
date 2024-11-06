
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# TODO: Make sure passed in key is STRING
# TODO: Make it available to clear from status keys which have not been updated in time frame.
# TODO: make it available to clear status for start of strings for values.
# TODO: Get keys and values for string starting with a set.

class StandardLogging():
    """
    Class to wrap the standard logging library with standard file and console setups.

    VERSION: 1.0
    CREATED: 2019-01-25

    """
    version = '2020-03-23'

    def __init__(self):
        self.line_format = ''
        self.set_format("%(asctime)s %(levelname)-8s [%(module)s] [%(funcName)s] %(message)s")
        self.log = logging.getLogger('__main__')
        self.log.setLevel(logging.DEBUG)
        self.log_output_type = 'file'
        self.level = ''        

    def set_level_info(self):
        self.log.setLevel(logging.INFO)
        self.set_format("%(asctime)s %(levelname)-8s %(message)s",u"%Y-%m-%d %H:%M:%S")
        return self

    def set_level_debug(self):
        self.log.setLevel(logging.DEBUG)
        self.set_format("%(asctime)s %(levelname)-8s [%(module)s] [%(funcName)s] %(message)s")
        return self
        
        '''        if level.upper() in ['DEBUG', 'WARN', 'INFO', 'ERROR', 'WARN']:
                    self.level = level.upper()
                    self.log.setLevel(logging.DEBUG)

                if self.level == 'INFO':
                    self.log.setLevel(logging.INFO)

                if self.level == 'WARN':
                    self.log.setLevel(logging.WARN)

                if self.level == 'ERROR':
                    self.log.setLevel(logging.ERROR)'''

    def set_format(self, line_format, dateformat="%Y-%m-%d %H:%M:%S"):
        self.line_format = logging.Formatter(line_format, dateformat)
        return self

    def setup_console(self):
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(self.line_format)
        self.log.addHandler(ch)

    def setup_file(self, folder, filename='log.log'):
        fh = logging.FileHandler(os.path.join(folder, filename))
        fh.setFormatter(self.line_format)
        self.log.addHandler(fh)
        return os.path.join(folder, filename)

    def setup_file_size_limit(self, folder, filename='log.log', max_kbytes=50):

        fh = RotatingFileHandler(os.path.join(folder, filename),
                                 mode='a',
                                 maxBytes=max_kbytes*1024,
                                 backupCount=2,
                                 encoding=None,
                                 delay=0)
        fh.setFormatter(self.line_format)
        self.log.addHandler(fh)

    def get(self):
        return self.log

    def get_console_logger(self):
        self.setup_console()
        self.log_header()
        return self.log

    def get_file_logger(self, folder, filename='log.log'):
        self.setup_file(folder, filename)
        self.log_header()
        return self.log

    def get_run_logger(self, folder, filename='log.log'):
        # Delete the file first
        if os.path.isfile(os.path.join(folder, filename)):
            os.remove(os.path.join(folder, filename)) # Delete the file is exists

        return self.get_file_logger(folder, filename)

    def get_file_rotating_logger(self, folder, filename='log.log', max_kbytes=50):
        self.setup_file_size_limit(folder, filename, max_kbytes)
        self.log_header()
        return self.log

    def log_header(self, message='STARTING'):
        self.log.info('## ' + message + ' ##')
