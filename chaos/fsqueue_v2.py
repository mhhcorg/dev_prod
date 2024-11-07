### Version 2 ###
# Author: Will  

import os 
import time 
import pickle
import random 
from pathlib import Path 
import uuid 

class fsqueue_v2: 

    def __init__(self, root, fs_wait=0.1, fifo=True):
        self._root = Path(root)
        self._root.mkdir(exist_ok=True, parents=True)
        self._wait = fs_wait
        self._fifo = fifo

    
    def get(self): 
        """
        changed from `os.walk()` to list all files, which is time consuming if there are multiple files in the directory containing many files 
        - `os.scandir()` is yields the directory entries one at a time (reads one by one instead of listing) and contains file metadata without the need to filly traverse the directory
        """

        while True: 
            with os.scandir(self._root) as entries: 
                files = [entry for entry in entries if entry.is_file() and not entry.name.endswith('.lock')]
            
            files = sorted(files, key = lambda e: e.name, reverse = not self._fifo)

            for entry in files: 
                fn = Path(entry.path)
                lock_path = fn.with_suffix('.lock')

                try: 
                    fn.rename(lock_path) # Lock the file by renaming 
                    with lock_path.open('rb') as f_obj: 
                        data = pickle.load(f_obj)
                    lock_path.unlink() # Remove the file after reading 
                    return data 
                
                except FileNotFoundError: 
                    pass # File was locked by another get() 

            time.sleep(self._wait)

    def put(self, data) :
        """
        changed time based calculations or random numbers because can still have potential issue with race conditions 
        - `uuid4()` ensures each filename is unique, highly unlikely to collide 
        """

        seq = str(uuid.uuid4())
        target = self._root / seq 
        fn = target.with_suffix('.lock')

        pickle.dump(data, fn.open('wb')) # Write the locked file 
        fn.rename(target) # Atomically unlock  

    def qsize(self):
        _, _, files = next(os.walk(self._root))
        n = 0
        for f in files:
            if f.endswith('lock'):
                continue  # Someone is reading the file
            n += 1
        return n

if __name__ == '__main__':
    q = fsqueue_v2('/tmp/test_queue')
    for i in range(10):
        q.put(f'data {i}')
    assert q.qsize() == 10
    for i in range(11):
        print(q.get())  # The last one should wait

