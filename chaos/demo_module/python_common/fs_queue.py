import os
import time
import pickle
import random

from pathlib import Path

class FSQueue:
    
    def __init__(self, root, fs_wait=0.1, fifo=True):
        """Creates a FSQueue that will store data as pickle files in root."""
        self._root = Path(root)
        self._root.mkdir(exist_ok=True, parents=True)
        self._wait = fs_wait
        self._fifo = fifo

    def put(self, data):
        """Adds data to the queue by dumping it to a pickle file."""
        now = int(time.time() * 10000)
        rnd = random.randrange(1000)
        seq = f'{now:016}-{rnd:04}'
        target = self._root / seq
        fn = target.with_suffix('.lock')
        pickle.dump(data, fn.open('wb'))  # Write to locked file
        fn.rename(target)  # Atomically unlock

    def get(self):
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
                    target = fn.with_suffix('.lock')
                    fn.rename(target)
                    data = pickle.load(target.open('rb'))
                    target.unlink()
                    return data
                except FileNotFoundError:
                    pass  # The file was locked by another get()
            # No files to read, wait a little bit
            time.sleep(self._wait)

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
    q = FSQueue('/tmp/test_queue')
    for i in range(10):
        q.put(f'data {i}')
    assert q.qsize() == 10
    for i in range(11):
        print(q.get())  # The last one should wait