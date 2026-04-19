import time
import psutil
import os

process = psutil.Process(os.getpid())

# To obtain number of cores in my laptop
num_cores = psutil.cpu_count()

def start():
    """
    Initializes the performance metrics since the metrics have to compare
    the state before and after the aggregation task is ran.
    """
    process.cpu_percent()
    process_before = process.cpu_times()
    start_time = time.time()
    
    return start_time, process_before

def stop(start_time, process_before):
    """
    Stops the performance metrics and actually computes the outputs.
    """
    elapsed = time.time() - start_time
    process_after = process.cpu_times()
    cpu_time = (process_after.user - process_before.user) + (process_after.system - process_before.system)
    cpu_percent = process.cpu_percent()
    cpu_percent_per_core = cpu_percent / psutil.cpu_count()

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# print(psutil.cpu_count())
