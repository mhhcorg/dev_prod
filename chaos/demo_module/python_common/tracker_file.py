import pickle
import os

class TrackerFile():

    def __init__(self, file_path):
        self.tracker_file = file_path
        self.tracker_data = []

    def get(self):       

        if len(self.tracker_data)>0:
            return self.tracker_data

        if os.path.exists(self.tracker_file):
            with open(self.tracker_file, 'rb') as f:
                self.tracker_data=pickle.load(f)
                return self.tracker_data

        return []
        
    def add(self, item):
        
        self.tracker_data = self.get()
        if item in self.tracker_data:
            return

        self.tracker_data.append(item)

        with open(self.tracker_file, 'wb') as f:
            pickle.dump(self.tracker_data,f)

if __name__ == "__main__":
    test_tracker = TrackerFile(r'U:\Projects\NextGen Import\test.pickle')

    test_tracker.add('test1')
    test_tracker.add('test2')
    test_tracker.add('test3')
    test_tracker.add('test4')
    test_tracker.add('test4')
    test_tracker.add('test4')
    test_tracker.add('test4')

    print(test_tracker.get())

    del test_tracker


    """ 6th """