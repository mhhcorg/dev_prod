""" 
    Custom File Lock

    Tool create a lock class used to create a lock file and release.

    Modified: 2024-05-26
    Note: Functional but has print statements which should come out after testing.

    2024-08-14 Add the test for is_locked and lock_file_exists
 """
import os
from pathlib import Path
import time

class CustomProcessLockFile():
    def __init__(self,file_path: str):
        self._lock_file=Path(file_path).with_suffix('.lock')
        self._locked = False

    def _stamp_file(self):
        try:
            with open(str(self._lock_file),"w") as f:
                f.write(str(os.getpid()))
            return True
        except:
            return False

    def aquire(self):
        if self._lock_file.exists() == False and self._locked == False:
            self._stamp_file()
            if self._lock_file.exists():
                self._locked = True
                print('Locked Successfully')
                return True
        else:
            print('Already locked or in use.')
            return False

    def release(self):
        if self._locked == False:
            #print('Not locked by this process. Cannot release')
            return False

        if self._lock_file.exists() == True:
            os.unlink(self._lock_file)

            if self._lock_file.exists() == False:
                self._locked = False
                print('Released')
                return True
            else:
                print('File Failed to Delete or Release.')
                return False
        else:
            print('File missing to delete.')
            self._locked = False
            return False
        
    def refresh_lock(self):
        if self._locked:
            return self._stamp_file()
        else:
            return False
        
    def lock_file_exists(self):
        if self._lock_file.exists() == False:
            self._locked = False
            return False
        else:
            return True
        
    def is_locked(self):
        if self._lock_file.exists() == True and self._locked == True:
            return True
        else:
            return False
        
    def __del__(self):
        self.release()
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        return None

    def __del__(self):
        self.release()
        return None
        
if __name__ == '__main__':
    lock = CustomProcessLockFile(str(Path(__file__)))
    lock.aquire()
    time.sleep(5)
    lock.release()