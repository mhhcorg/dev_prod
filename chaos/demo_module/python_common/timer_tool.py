import time
import sys
from datetime import datetime

class TimerTool():

    def __init__(self):
        self.timers = {}

    def start(self,timer_name='default'):
        self._setup_timer(timer_name)
        self.timers[timer_name]['start_time'] = time.perf_counter()
        self.timers[timer_name]['end_time'] = None
        self.timers[timer_name]['result'] = 0

    def stop(self, timer_name='default', words=False):
        if not (timer_name in self.timers):
            raise

        self.timers[timer_name]['end_time'] = time.perf_counter()
        self.timers[timer_name]['result'] = self.timers[timer_name]['end_time']-self.timers[timer_name]['start_time']
        self.timers[timer_name]['result_string'] = self._seconds_to_string(float(self.timers[timer_name]['result']))

        if words == False:
            return round(self.timers[timer_name]['result'],5)
        else:
            return self.result_string(timer_name)
            
    def result(self,timer_name='default'):
        return self.timers[timer_name]['result']
    
    def result_string(self,timer_name='default'):

        result = self.timers[timer_name]['result']
        

    def _seconds_to_string(self,result):
        hours = round(result//3600)
        minutes = round((result%3600)//60)
        seconds = round((result%3600)%60,3)

        if hours > 0:
            return f'{hours} hours {minutes} minutes {seconds} seconds'
        elif minutes > 0:
            return f'{minutes} minutes {seconds} seconds'
        else: 
            return f'{seconds} seconds'

    def _setup_timer(self,timer_name='default'):
        if not (timer_name in self.timers):
            self.timers[timer_name]={"start_time":0,"end_time":0, "result:":0,"result_string":""}

            
if __name__ == "__main__":
    
    timers = TimerTool()

    timers.start('test1')
    print(timers.stop('test1',True))
    timers.start('test2')
    print(timers.stop('test2'))

    del timers

    script_timer = TimerTool()
    script_timer.start()
    script_timer.stop()
    script_timer.r
    

