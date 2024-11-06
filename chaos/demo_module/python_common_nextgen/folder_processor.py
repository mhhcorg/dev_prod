import os
import re
import sys
import logging
import datetime

'''
    Folder Action Item Parser

    This will cycle through folders finding out which contains scripts and begin to execute them in order logging the data centrally.
'''

class FolderProcessor():

    def __init__(self):
        
        self.pathname = ''
        self.log = ''
        self.interator = 0
        self.paths = []
        self.actions = []
        self.line_format = logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(module)s] [%(funcName)s] %(message)s")
        self.log = logging.getLogger('__main__')
        self.log.setLevel('INFO')

    # SET LOGGER
    def set_logger(self, new_logger, level='INFO'):
        self.log = new_logger
        self.log.setLevel(level)
    
    def get_immediate_subdirectories(self, a_dir):
        # self.log.info(str(a_dir))
        return [name for name in os.listdir(a_dir)
                if os.path.isdir(os.path.join(a_dir, name))]

    def set_folder_path(self, new_path):
        self.pathname = new_path 

    def get_execution_folders(self, path):
        #self.log.info('Checking Folder:' + path)
        #self.log.info(path)

        for folder in self.get_immediate_subdirectories(path):
            if re.match("STEP\_\d{2,3}.*", folder):

                # Check if it is a direct path or group
                match = re.search("STEP\_\d{2,3}\_?([a-zA-Z]*)_?.*", folder)
                if match:
                    # print(type(str(match.group(1)).lower()))
                    if str(match.group(1)).lower() in ['get', 'put', 'process', 'trigger', 'detect_change', 'notify']:
                        self.log.info('Step: ' + os.path.join(path, folder) + ' for action ' + match.group(1).lower())
                        self.paths.append(os.path.join(path, folder))
                        self.actions.append(match.group(1).lower())
                    else:
                        #self.log.info('Step Container:' + folder)
                        #self.paths.extend(self.get_execution_folders(os.path.join(path, folder)))
                        self.get_execution_folders( os.path.join(path, folder))
                else:
                    # Check the sub folder for actionable folder
                    self.paths.extend(self.get_execution_folders(os.path.join(path, folder)))

            if folder.lower() in ['get', 'put', 'process', 'trigger', 'detect_change', 'notify', 'view']:
                self.log.info('Step: ' + os.path.join(path, folder) + ' for action ' + folder.lower())
                self.paths.append(os.path.join(path, folder))
                self.actions.append(folder.lower())

        return self.paths

    def run(self):
        return self.get_execution_folders(self.pathname)

    def get_actions(self):
        return self.actions

    def get_paths(self):
        return self.paths

