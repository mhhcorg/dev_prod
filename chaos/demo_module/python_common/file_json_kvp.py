from pathlib import Path
import json
from datetime import datetime

class FileJSONKVP():
    def __init__(self,file_path: str):
        self._data = {}
        self._file_path = Path(file_path)
    
    def _load_file(self):
        if self._file_path.exists():
            with open(self._file_path, 'r') as f:
                self._data = json.loads(f.readlines())

    def _get_timestamp(self):
        return datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
    
    def _save_file(self):
        if self._file_path.exists()==False:
            self._data['meta_created_at'] = self._get_timestamp()

        with open(self._file_path, 'w') as f:
            f.write(json.dumps(self._data))

    def set(self,key:str,value):
        self._data[key.lower().strip()] = value
        self._data['meta_modified_at'] = self._get_timestamp()
        self._save_file()

    def keys(self):
        return list(self._data.keys())
    
    def export_dict(self):
        return self._data
    
    def get(self, key, value_if_empty=None):
        return self._data.get(key,value_if_empty)

if __name__ == '__main__':

    kvp = FileJSONKVP(Path(__file__).with_suffix('.kvp.json'))

    kvp.set('Test1','Value1')
    kvp.set('Test2','Value2')
    kvp.set('Test3',{'Value3':True})
    kvp.set('Test4','Value4')

    print(kvp.get('Test1'))
    print(kvp.get('Test2'))
    print(kvp.get('Test3'))
    print(kvp.get('Test4'))

    print(str(type(kvp.get('Test3'))))
    print(kvp.keys())