import time
import psutil
import os

process = psutil.Process(os.getpid())

def start():
    process_before = process.cpu_times()
    start_time = time.time()

    return start_time, process_before

def stop(start_time, process_before):
    elapsed = time.time() - start_time
    process_after = process.cpu_times()
    cpu_time = (process_after.user - process_before.user) + (process_after.system - process_before.system)

    return elapsed, cpu_time
