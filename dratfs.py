import time
import os
from color import color
from print_log import print_log
import signal
import threading

def signal_handler(a, b):
    print(f"Signal {a} from frame {b}")
    print("after wait 10s in signal handler")
    new_thread.start()

def thread_job(a):
    print("this is thread_job")
    time.sleep(10)
    print("after 10s in thread_job")

data = 10

new_thread = threading.Thread(target=thread_job, args=(data,))

signal.signal(signal.SIGINT, signal_handler)

# sigset = [signal.SIGINT]

# signal.sigwait(sigset)

signal.pause()

print("This line is after sigwait")

print("This is in the finally")
new_thread.join()
print("quit main thread")