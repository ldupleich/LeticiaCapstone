"""
This script contains the metrics that will be extracted upon running the
various aggregation tasks:
    - Execution (elapsed) time
    - CPU use (per core for Polars, overall for SQL)
    - CPU time

Execution time and CPU time are both outputted in milliseconds, and CPU use is
outputted as a percentage.

This file is imported into "polars_aggregation", and runs automatically
when "polars_aggregation" runs, so it does not have to be executed individually.

Sources:
- https://www.geeksforgeeks.org/python/psutil-module-in-python/
- https://psutil.readthedocs.io/stable/
- https://pypi.org/project/psutil/
- https://docs.python.org/3/library/time.html 
"""

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
    elapsed = (time.time() - start_time) * 1000
    process_after = process.cpu_times()
    cpu_time = ((process_after.user - process_before.user) + (process_after.system - process_before.system)) * 1000
    cpu_percent = process.cpu_percent()
    cpu_percent_per_core = cpu_percent / psutil.cpu_count()

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# print(psutil.cpu_count())
