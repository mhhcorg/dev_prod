"""
    FS Queue JSON

    File System Based Queue Using JSON Files

    This is the base library used by the query and the worker to append and pull items from the queue.

    2024-05-24
    2024-05-28 Fixed get to continue if it fails to get an item.
    2024-07-09 Added incrementer to the script to solve very fast entried which may sort in correctly.
"""


import os
import time
import random
import hashlib
import json

""" 2023-09-07 - Added a function to exit if the queue is empty """

from pathlib import Path

class FSQueueJSON:

    def __init__(self, root, fs_wait=0.1, fifo=True):
        """Creates a FSQueue that will store data as a files in root."""
        self._root = Path(root)
        self._root.mkdir(exist_ok=True, parents=True)
        self._wait = fs_wait
        self._fifo = fifo
        self._counter = 0

    def _get_increment(self):
        if self._counter < 9999:
            self._counter+=1
        else:
            self._counter = 1
        return self._counter

    def _get_queue_file_name(self,data):
        if self._fifo:
            now = int(time.time() * 10000000)
            rnd = random.randrange(1000)
            increment = self._get_increment()
            seq = f'{now:017}-{increment:04}-{rnd:04}'
            return self._root / seq
        else:
            return self._root / hashlib.sha256(data.encode('utf-8')).hexdigest()

    def put(self, data: str):

        # Convert Dict to JSON
        if isinstance(data, dict):
            data = json.dumps(data)
        
        # Get the name and location of the file
        target = self._get_queue_file_name(data)
        
        try:
            fn = target.with_suffix('.lock')
            if not target.exists():
                fn.write_text(data)
                fn.rename(target.with_suffix(".json"))  # Atomically unlock
        except:
            raise

    def get(self, wait_if_empty=True, next_on_error=True):
        """Pops data from the queue, unpickling it from the first file."""
        # Get files in folder and reverse sort them
        while True:
            _, _, files = next(os.walk(self._root))
            files = sorted(files, reverse=not self._fifo)
            for f in files:
                if f.endswith('lock'):
                    continue  # Someone is writing or reading the file

                try:
                    fn = self._root / f

                    # Rename to lock it for reading
                    target = fn.with_suffix('.lock')
                    
                    if target.exists():
                        continue
                    
                    try: 
                        fn.rename(target)
                    except:
                        # TODO: This could get logged
                        continue
              
                    data = target.read_text()
                    try:
                        target.unlink()
                    except:
                        # TODO: This should be logging to parent script
                        print(f"Failed to Delete {f}")
                    return data
                except FileNotFoundError:
                    pass  # The file was locked by another get()
            
            # Check if it should wait until a new item pops in.
            if wait_if_empty:
                # No files to read, wait a little bit
                time.sleep(self._wait)
            else:
                return None

    def qsize(self):
        """Returns the approximate size of the queue."""
        _, _, files = next(os.walk(self._root))
        n = 0
        for f in files:
            if f.endswith('lock'):
                continue  # Someone is reading the file
            n += 1
        return n

if __name__ == '__main__':
    q = FSQueueJSON('/tmp/test_queue')
    for i in range(10):
        q.put(f'data {i}')
    assert q.qsize() == 10
    for i in range(11):
        print(q.get())  # The last one should wait