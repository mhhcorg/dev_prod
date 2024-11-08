import os 
import time 
import pickle
from pathlib import Path 
import uuid 
import json 
import logging 

class fsqueue_v2:
    """
    Updates: 
    - json or pickle file serialization 
    - improved with checks similarly employed in `FSQueueJson`   
    """
    def __init__(self, root, fs_wait=0.1, fifo=True, use_json=False):
        """
        Initializes the FSQueue with an option to use either pickle or JSON for serialization.
        """
        self._root = Path(root)
        self._root.mkdir(exist_ok=True, parents=True)
        self._wait = fs_wait
        self._fifo = fifo
        self.use_json = use_json

    def get(self, wait_if_empty=True):
        """
        Retrieves data from the queue. Uses JSON or Pickle to deserialize depending on the flag set during initialization.
        """
        while True:
            with os.scandir(self._root) as entries:
                files = [entry for entry in entries if entry.is_file() and not entry.name.endswith('.lock')]

            files = sorted(files, key=lambda e: e.name, reverse=not self._fifo)

            for entry in files:
                fn = Path(entry.path)
                lock_path = fn.with_suffix('.lock')

                try:
                    # Check if the file is already locked
                    if lock_path.exists():
                        continue

                    # Attempt to rename to lock it
                    try:
                        fn.rename(lock_path)
                    except FileNotFoundError:
                        # If the file is already locked or removed, continue
                        logging.warning(f"File {fn} was not found or already locked by another process.")
                        continue

                    # Read the file content
                    with lock_path.open('r' if self.use_json else 'rb') as f_obj:
                        if self.use_json:
                            data = json.load(f_obj)
                        else:
                            data = pickle.load(f_obj)

                    # Attempt to delete the file after reading
                    try:
                        lock_path.unlink()
                    except Exception as e:
                        logging.error(f"Failed to delete the file {lock_path}: {e}")

                    return data

                except Exception as e:
                    logging.error(f"Unexpected error occurred while processing file {fn}: {e}")

            # If the queue is empty, determine whether to wait or return None
            if wait_if_empty:
                time.sleep(self._wait)
            else:
                return None

    def put(self, data):
        """
        Adds data to the queue. Uses JSON or Pickle to serialize depending on the flag set during initialization.
        """
        seq = str(uuid.uuid4())
        target = self._root / seq
        fn = target.with_suffix('.lock')

        try:
            with fn.open('w' if self.use_json else 'wb') as f:
                if self.use_json:
                    json.dump(data, f)
                else:
                    pickle.dump(data, f)

            # Rename to unlock the file atomically
            fn.rename(target)

        except Exception as e:
            logging.error(f"Failed to write data to file {fn}: {e}")
            raise

    def qsize(self):
        """
        Returns the approximate size of the queue.
        """
        try:
            with os.scandir(self._root) as entries:
                files = [entry for entry in entries if entry.is_file() and not entry.name.endswith('.lock')]
            return len(files)
        except Exception as e:
            logging.error(f"Failed to calculate queue size: {e}")
            return 0

if __name__ == '__main__':
    q = fsqueue_v2('/tmp/test_queue')
    for i in range(10):
        q.put(f'data {i}')
    assert q.qsize() == 10
    for i in range(11):
        print(q.get())  # The last one should wait