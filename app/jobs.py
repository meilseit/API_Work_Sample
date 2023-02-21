import time
import random 

#define dummy async task that just waits for a random interval of time
def complex_task():
    interval = random.randint(15, 40)
    time.sleep(interval)
    return interval