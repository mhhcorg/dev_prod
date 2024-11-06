""" 
    2024-08-23
"""
from pathlib import Path
from datetime import datetime
import json

class FileSignal():

    def __init__(self, path: str, name: str):
        self.path = str(path)
        self.name = name
        self.file_path = (Path(path) / name).with_suffix('.sig')
        self.data = None

    def set(self, message:str = None):
        if Path(self.file_path).exists():
            return True
        
        try: 
            with open(self.file_path,'w') as f:
                self.data = {'path': str(self.path), 'name': self.name,'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                json.dump(self.data, f, indent=4)
            return True
        except:
            return False

    def unset(self):
        try:
            if Path(self.file_path).exists():
                Path(self.file_path).unlink()
            return True
        except:
            return False
    
    def is_set(self):
        try:
            if Path(self.file_path).exists():
                return True
            else:
                return False
        except:
            return False
        
    def get(self):
        if self.is_set() == True:
            try:
                with open(self.file_path,'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _load(self):
        if self.is_set():
            try:
                with open(self.file_path,'r') as f:
                    self.data=json.load(f)
                
            except:
                self.data = None
                return None
        
stop_signal = FileSignal(r'N:\\Automation\\Temp','test_nextgen_load_stop')
#stop_signal.unset()
print(stop_signal.is_set())
#stop_signal.set()