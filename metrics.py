import time
import psutil
import os

process = psutil.Process(os.getpid())
start_time = None
cpu_before = None

def start():
    psutil.cpu_percent(percpu=True)
    process.cpu_percent()
    start_time = time.time()
    
    return start_time

def stop(start_time):
    elapsed = time.time() - start_time
    cpu_per_core = cpu_per_core = psutil.cpu_percent(percpu=True)
    cpu_process = process.cpu_percent()

    return elapsed, cpu_per_core, cpu_process

