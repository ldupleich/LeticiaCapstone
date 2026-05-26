"""
This script runs the Polars-based aggregation tasks across the selected three complexity levels:
    1. Single-table (no join statements)
    2. Two-tables (one join statement)
    3. Three-tables (two join statements)

The script first preprocesses the data (null removal, outlier removal, and duplicate checking) using
the in-house functions in the file polars.preprocessing from this same directory. Then, the aggregation
tasks are run.

Each task is executed 100 times (n=100), and for each execution, the execution time, CPU time, and CPU
percentage are recorded. The results are exported to CSV files for further analysis.

Given that Polars makes use of multi-core parallelism, the CPU percent recorded in these aggregation
tasks are the CPU percent per CPU core. 

There are several print statements that have been commented out. These were used for checking the
correctness of the program. I have left these to show some of the process of creating this file.

Sources:
- https://docs.pola.rs/user-guide/concepts/lazy-api/
- https://docs.pola.rs/api/python/dev/reference/lazyframe/api/polars.LazyFrame.join.html
- https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.join.html
- https://docs.pola.rs/user-guide/expressions/aggregation/
- https://docs.pola.rs/user-guide/transformations/joins/
- https://docs.pola.rs/api/python/stable/reference/series/api/polars.Series.dt.month.html
- https://docs.python.org/3/library/csv.html
"""

import polars as pl
import metrics
import psutil
import csv
import polars_preprocessing as pp

n = 100

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESS

dataframes = pp.load_data()
dataframes = pp.remove_nulls(dataframes)
dataframes = pp.remove_outliers(dataframes)
dataframes = pp.check_duplicates(dataframes)

# print("Row counts AFTER preprocessing:")
pp.row_counts(dataframes)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 1: Single table aggregation tasks

# Single table 1
def single_table_1(dataframes):
    """
    Groups patients by gender.
    """
    
    start_time, process_before = metrics.start()

    result = (
        dataframes["Patients"]
        .lazy() # recommended instead of eager
        .group_by("Gender")
        .agg(pl.len())
        .collect()
    )
    # print(result1)
    print(f"Number of patients grouped by gender: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    
    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU time: {cpu_time:.4f}s")

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Single table 2
def single_table_2(dataframes):
    """
    Groups number of surgeries by surgery type.
    """
    
    start_time, process_before = metrics.start()

    result = (
        dataframes["SurgeryRecord"]
        .lazy() # recommended instead of eager
        .group_by("surgery_Type")
        .agg(pl.len())
        .collect()
    )
    # print("\n")
    # print(result2)
    print(f"Number of surgeries grouped by surgery type: {len(result)}")
    
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)

    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU time: {cpu_time:.4f}s")

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Saving results
time_rows_single = []
cpu_percent_rows_single = []
cpu_time_rows_single = []

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_1(dataframes)
    time_rows_single.append(["patients_by_gender", i, elapsed])
    cpu_percent_rows_single.append(["patients_by_gender", i, cpu_percent_per_core])
    cpu_time_rows_single.append(["patients_by_gender", i, cpu_time])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_2(dataframes)
    time_rows_single.append(["surgeries_by_type", i, elapsed])
    cpu_percent_rows_single.append(["surgeries_by_type", i, cpu_percent_per_core])
    cpu_time_rows_single.append(["surgeries_by_type", i, cpu_time])

# Creating output .csv files
f = open("single_time_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_ms"])
writer.writerows(time_rows_single)
f.close()

f = open("single_cpu_percent_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_single)
f.close()

f = open("single_cpu_time_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_time_ms"])
writer.writerows(cpu_time_rows_single)
f.close()

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 2: Multi-table (two) aggregation tasks

# Two-table 1
def two_table_1(dataframes):
    """
    Number of doctors per department.
    """
    
    start_time, process_before = metrics.start()

    result = (
        dataframes["Doctor"]
        .lazy()
        .join(dataframes["Department"].lazy(), on="dept_Id", how="inner")
        .group_by("dept_Name")
        .agg(pl.len())
        .collect()
    )

    print(f"Number of doctors per department: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Two-table 2
def two_table_2(dataframes):
    """
    Number of appointments by patient.
    """
    
    start_time, process_before = metrics.start()

    result = (
        dataframes["Appointment"]
        .lazy()
        .join(dataframes["Patients"].lazy(), on="patient_Id", how="inner")
        .group_by(["patient_Id", "FName", "LName"])
        .agg(pl.len())
        .collect()
    )

    print(f"Number of appointments per patient: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Saving results
time_rows_two = []
cpu_percent_rows_two = []
cpu_time_rows_two = []


for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = two_table_1(dataframes)
    time_rows_two.append(["doctors_per_dept", i, elapsed])
    cpu_percent_rows_two.append(["doctors_per_dept", i, cpu_percent_per_core])
    cpu_time_rows_two.append(["doctors_per_dept", i, cpu_time])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = two_table_2(dataframes)
    time_rows_two.append(["appointments_per_patient", i, elapsed])
    cpu_percent_rows_two.append(["appointments_per_patient", i, cpu_percent_per_core])
    cpu_time_rows_two.append(["appointments_per_patient", i, cpu_time])

# Creating output .csv files
f = open("two_time_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_ms"])
writer.writerows(time_rows_two)
f.close()

f = open("two_cpu_percent_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_two)
f.close()

f = open("two_cpu_time_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_time_ms"])
writer.writerows(cpu_time_rows_two)
f.close()

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 3: Multi-table (three-or-more) aggregation tasks

# Three-table 1
def three_table_1(dataframes):
    """
    Number of surgeries per department per month.
    """
    
    start_time, process_before = metrics.start()

    result = (
        dataframes["SurgeryRecord"]
        .lazy()

        # Have different names for the key so we need left_on and right_on
        .join(dataframes["Doctor"].lazy(), left_on="surgeon_Id", right_on="doct_Id", how="inner")
        .join(dataframes["Department"].lazy(), on="dept_Id", how="inner")
        .with_columns(pl.col("surgery_Date").dt.month())

        # Extract month
        .group_by("dept_Name", "surgery_Date")
        .agg(pl.len())
        .collect()
    )

    print(f"Number of surgeries per department per month: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Three-table 2
def three_table_2(dataframes):
    """
    Number of appointments per doctor per department
    """
    
    start_time, process_before = metrics.start()

    result = (
        dataframes["Appointment"]
        .lazy()
        .join(dataframes["Doctor"].lazy(), on="doct_Id", how="inner")
        .join(dataframes["Department"].lazy(), on="dept_Id", how="inner")
        .group_by(["dept_Name", "doct_Id", "FName", "LName"])
        .agg(pl.len())
        .collect()
    )

    print(f"Number of appointments per doctor per department: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Saving results
time_rows_three = []
cpu_percent_rows_three = []
cpu_time_rows_three = []

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = three_table_1(dataframes)
    time_rows_three.append(["surgeries_per_dept_per_month", i, elapsed])
    cpu_percent_rows_three.append(["surgeries_per_dept_per_month", i, cpu_percent_per_core])
    cpu_time_rows_three.append(["surgeries_per_dept_per_month", i, cpu_time])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = three_table_2(dataframes)
    time_rows_three.append(["appointments_per_doctor_per_dept", i, elapsed])
    cpu_percent_rows_three.append(["appointments_per_doctor_per_dept", i, cpu_percent_per_core])
    cpu_time_rows_three.append(["appointments_per_doctor_per_dept", i, cpu_time])

# Creating output .csv files
f = open("three_time_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_ms"])
writer.writerows(time_rows_three)
f.close()

f = open("three_cpu_percent_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_three)
f.close()

f = open("three_cpu_time_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_time_ms"])
writer.writerows(cpu_time_rows_three)
f.close()

