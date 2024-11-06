""" 
    File Record DB
    2024-08-23
"""
import json
import csv
from pathlib import Path
from datetime import datetime
from filelock import FileLock

class FileRecordDB:

    def __init__(self, folder_path: str) -> None:
        self.folder_path = Path(str(folder_path).lower())
        self.folder_path.mkdir(parents=True, exist_ok=True)
        self.key_field_name = '_key'
        self.version_field_name = '_version'
        self.created_field_name = '_created_at'
        self.modified_field_name = '_modified_at'

    def _ymdhms(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _fill_record(self, key, record):
        
        if self.modified_field_name not in record.keys():
            record[self.modified_field_name] = self._ymdhms()

        if self.created_field_name not in record.keys():
            record[self.created_field_name] = self._ymdhms()

        if self.version_field_name not in record.keys():
            record[self.version_field_name] = 1

        if self.key_field_name not in record.keys():
            record[self.key_field_name] = key

        return record
    
    def _clean_key(self, value: str):
        try:
            result = value.lstrip().rstrip().lower()
            if len(result)==0:
                return None
            return result
        except:
            return None
        
    def patch_record(self, data: dict, key:str = None):
        return self._upsert(data,key)

    def _upsert(self, data: dict, key:str=None):
        """ 
            Apply only the passed in data over the existing record.
            Create the record if non exists.
        """
        if key == None:
            key = data.get([self.key_field_name])

        # If No Record, then create it.
        if self.record_exists(key) == False:
            return self.set_record(key, data)

        try:
            lock = FileLock(str(self._record_file_path(key)) + '.lock')

            if lock.acquire(timeout=2):
                try: 
                    with open(self._record_file_path(key), 'r+') as f:
                        record = json.load(f)
                        record_edited_flag = False 
                        for field, value in data.items():
                            if record.get(field,'') != value:
                                record[field] = value
                                record_edited_flag = True

                        # Increment Version if exit occured
                        if record_edited_flag == True:
                            record[self.version_field_name] = record.get(self.version_field_name,1)+1
                            record[self.modified_field_name] = self._ymdhms()
                        
                        f.seek(0)
                        json.dump(record, f, sort_keys = True, indent = 4)
                        f.truncate()
                        return True
                except:
                    return False
                finally:
                    lock.release()
            return True
        except:
            return False

    def _save_record(self, key:str, data:dict):

        if self.modified_field_name not in data.keys():
            data[self.modified_field_name] = self._ymdhms()

        if self.created_field_name not in data.keys():
            data[self.created_field_name] = self._ymdhms()

        data[self.key_field_name] = key.lower()

        try:
            with open(self._record_file_path(key), 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4)
            return True
        except:
            return False

    def add_key(self, key):
        return self._create_record(key)

    def set_field(self, key:str, field:str, value):

        if len(field) == 0:
            return False
        if len(key) == 0:
            return False

        update = {field.lower(): value}
        return self._upsert(update,key.lower())

    def set_record(self, key:str, record: dict):

        if isinstance(record, dict) == False:
            return False
        
        if isinstance(key, str) == False:
            return False
        
        record = self._fill_record(key.lower(), record)

        try:
            with open(self._record_file_path(key), 'w') as f:
                json.dump(record, f, sort_keys=True, indent=4)
            return True
        except:
            return False
        
    def get_field(self, key: str, field: str, default=None):
        record = self.get_record(key)
        if record == None:
            return default
        
        return record.get(field, default)
        
    def get_record(self, key: str, default: dict = None):
        key = self._clean_key(key)

        try:
            with open(self._record_file_path(key), 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            if default!=None:
                return default
            else:
                return None

    def get_keys(self) -> list:
        files = []
        for file_path in self.folder_path.iterdir():
            if Path(file_path).is_file():
                files.append(Path(file_path).stem)
        return files
    
    def _record_file_path(self, key:str) -> Path:
        key = self._clean_key(key)
        assert key != None
        return Path(self.folder_path / key).with_suffix('.json')
    
    def record_exists(self,key: str):
        key = self._clean_key(key)

        if Path(self._record_file_path(key)).exists():
            return True
        else:
            return False

    def field_exists(self, key, field):
        key = self._clean_key(key)
        field = self._clean_key(field)

        data = self.get_record(key)

        if data.get(field) == None:
            return False
        else:
            return True 

    def save(self):
        pass

    def get(self, key=None, field=None, **kwargs):
        key = self._clean_key(key)
        field = self._clean_key(field)

        default = kwargs.get('default',None)

        if key == None:
            return self.get_keys()
        elif field == None:
            return self.get_record(key, default)
        else:
            return self.get_field(key, field, default)
    
    def _keys(self):
        return sorted(f for f in self.folder_path.iterdir() if f.is_file())

    def _columns(self):
        columns = []
        try:
            for key in self.get_keys():
                record = self.get_record(key)
                if record == None:
                    print(f'Record [{self.folder_path}\\{key}] is invalid. Skipping.')
                    continue

                for field in record.keys():
                    if field in columns:
                        continue
                    columns.append(field)

            return columns  
            #columns = list(set(columns))
        except Exception as e:
            print(e)
            return False
        
    def to_list(self, columns =None):
        """ 
            columns (list):
            Optional filter or full list of columns to include the list.  Blank means it will export all columns in the data.
           """
        if columns == None:
            columns = self._columns()

        data = []

        for key in self.get_keys():
            row = {self.key_field_name: key}
            record = self.get_record(key)
            for field in columns:
                row[field] = record.get(field,'')

            data.append(row)
            del row

        return data

    def to_csv(self, file_path: str, columns=None):
        if columns == None:
            columns = self._columns()
        data = self.to_list(columns)

        if data == None or columns == None:
            return False
        try:
            with open(file_path, 'w', newline='\n') as f:
                writer=csv.DictWriter(f,fieldnames=columns)
                writer.writeheader()
                writer.writerows(data)
            return True
        except:
            return False
    
    def _autosave(self):
        pass

    def _create_record(self,key):
        key = self._clean_key(key)

        if self.record_exists(key) == True:
            return False
        
        record = self._fill_record(key, {})
        
        self._save_record(key, record)
        return True
    
    def delete_record(self,key: str):
        key = self._clean_key(key)

        try:
            Path(self._record_file_path(key)).unlink()
            return True
        except:
            return False
        
    def delete_field(self, key: str, field: str):

        key = self._clean_key(key)
        field = self._clean_key(field)

        if self.record_exists(key) == False:
            return False

        if self.field_exists(key,field) == False:
            return True

        try:
            lock = FileLock(str(self._record_file_path(key)) + '.lock')

            if lock.acquire(timeout=2):
                try:
                    with open(self._record_file_path(key), 'r+') as f:
                        record = json.load(f)
                        del record[field]
                        f.seek(0)
                        json.dump(record, f, sort_keys = True, indent = 4)
                        f.truncate()
                    return True
                except:
                    return False
                finally:
                    lock.release()
        except:
            return False
    
    def __len__(self):
        return len(self.get_keys())

    def __name__(self):
        return self.folder_path

    def __exit__(self):
        pass


if __name__ == "__main__":

    db = FileRecordDB(r'C:\\Users\\dacolon\\Desktop\\FileDB')

    db.set_record('record_id',{'table_name': 'account','detail':'test'})

    db.get_record('record_id')

    db.set_field('record_id','f1','v1')
    db.set_field('record_4','f2','v2')
    db.set_field('record_id','f3','v3')

    print(db.get_record('record_id'))

    db.delete_field('record_id','detail')
    db.delete_field('record_4','f1')
    db.delete_field('record_3','f2')

    db.set_record('record_id',{})
    db.delete_record('record_id')

    print(db.get_record('record_id'))
    print(db.get('record_id','f3', default='Something'))
    print(db.get('record_id','_version', default='Bla Bla'))
    print(db.get_keys())

    db.delete_record('record_3')
    print(db.get_keys())
