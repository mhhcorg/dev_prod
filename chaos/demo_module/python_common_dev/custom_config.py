import configparser
import os
import sys
import time
import datetime 

class CustomConfig():

    def __init__(self,path,filename='config.ini', main_section='global'):

        self.filepath = os.path.join(path,filename)
        self.config = configparser.RawConfigParser(allow_no_value=True)
        self.autosave_enabled = 0
        self.default_section = main_section

        if os.path.isfile(self.filepath) == False:
            #print('creating ini',self.filepath)
            self.config.add_section(main_section)
            self.config.set(main_section,'NAME','INI')
            self.config.set(main_section,'config.created_at',str(datetime.datetime.now()))
            self.save()
        else:
            self.config.read(self.filepath)
            #print('sections',str(self.config.sections()))
            #print('has section',self.config.has_section(main_section))
            if self.config.has_section(main_section) == False:
                #print('missing section ini',main_section)
                self.config.add_section(main_section)

    def enable_autosave(self):
        self.autosave_enabled = 1
        self.save()

    def autosave(self):
        if self.autosave_enabled == 1:
            self.save()

    def get(self, option, default='', section='global'):
        if self.config.has_option(section, option) == True:
            #print('Found Setting')
            return self.config.get(section, option.lower() )
        else:
            return default

    def put(self, option, value, section='global'):
        self.config.set(section, option.lower(), str(value))
        self.autosave() # Save if set to autosave.
    
    def set(self, option, value, section='global'):
        self.config.set(section, option.lower(), value)
        self.autosave() # Save if set to autosave.

    def get_or_set(self, option, value, section='global'):
        result = self.get(option,'',section)
        if result == '':
            print('test',result)
            self.set(option,value,section)
            return value
        else:
            return result

    def delete(self, option, section = 'global'):
        try: 
            self.config.remove_option( section, option.lower() )
        except configparser.NoOptionError:
            pass

    def get_options(self, section='global'):
        return self.config.options(section)

    def has_value(self, option, section = 'global'):
        value = self.get(option,'',section)
        if value == '':
            return False
        else:
            return True

    def get_override(self, option):
        override_value = self.get(option,'','override')
        if override_value == '':
            return self.get(option,'','global')
        else:
            return override_value

    def delete_override(self,option):
        self.config.remove_option('override',option)

    def set_override(self, option, value):
        self.config.set('override',option,value)
    
    def get_all(self, section = 'GLOBAL'):
        return self.config.items('section')
    
    def save(self):
        print('Saving',self.filepath)
        self.config.set('global', 'config.modified_at', str(datetime.datetime.now()))
        try: 
            self.config.write(open(self.filepath,'w'))

        except Exception as e:
            # TODO: Do better than this. No printing out.
            print(str(e))
            raise
