""" KeyRecord Class

    2023-10-05 - Added Autosave option.
 """

from configparser import ConfigParser
import os

class KeyRecord:
    def __init__(self, filepath, autosave=True) -> None:
        self.filepath = filepath
        self.config = ConfigParser()

        self.autosave_flag = autosave
        self.last_key = ''

        if os.path.exists(filepath):
            self.config.read(self.filepath)
        else:
            self.save()

    def add_key(self, key):
        self._create_record(key)
        self._autosave()

    def set_field(self,key,field,value):
        self._create_record(key)
        self.config.set(key,field,str(value))
        self._autosave()

    def set_record(self,key,record):
        for field in record:
            self.set_field(key,field,record[field])
        self._autosave()

    def get_field(self, key, field, default=''):
        if not self.config.has_section(key):
            return default
    
        if not self.config.has_option(key,field):
            return default
        
        return self.config.get(key,field,fallback=default)
        
    def get_record(self, key):
        self._create_record(key)

        items = self.config.items(key)
    
        result = {}
        for item in items:
            field, value = item
            result[field]=value

        return result

    def get_keys(self):
        return self.config.sections().sort()
    
    def record_exists(self,key):
        if key in self.config.has_section(key):
            return True
        else:
            return False

    def field_exists(self,key,field):
        if field in self.config.has_option(key,field):
            return True
        else:
            return False

    def save(self):
        with open(self.filepath,'w') as f:
            self.config.write(f)

    def get(self, key='',field=''):
        if key=='':
            return self.get_keys()
        elif field=='':
            return self.get_record(key)
        else:
            return self.get_field(key,field)
    
    def _autosave(self):
        if self.autosave_flag:
            self.save

    def _create_record(self,key):
        self.last_key = key
        if not key in self.config.sections():
            self.config.add_section(key)
    
    def __len__(self):
        return len(self.config.sections())

    def __name__(self):
        return self.filepath

    def __exit__(self):
        self.save()

if __name__ == "__main__":

    db = KeyRecord(r'C:\Users\dacolon\Desktop\test.ini',False)
    db.set_field('key1','f1','v1')
    db.set_field('key1','f2','v2')
    db.set_field('key1','f3','v3')

    db.set_field('key2','f1','v1')
    db.set_field('key2','f2','v2')
    db.set_field('key2','f3','v3')
    db.set_field('key3','f3','v3')

    #print(db.get_record('key'))
    #print(db.get_record('key2'))
    #print(db.get_record('key3'))


    #print(db.get_field('key','f1'))

    db.save()

    """ db.get_field('key','subfield','default')
    db.set_record('key',record)
    db.delete_record('key')
    db.get_keys()
    db.get_db()
    db.save('filename')
    """

    r1 = db.get_record('key1')

    db.set_record('key5',r1)

    print(db.get_record('key5'))
