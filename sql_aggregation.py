"""
This script runs the SQL-based aggregation tasks across the selected three complexity levels:
    1. Single-table (no join statements)
    2. Two-tables (one join statement)
    3. Three-tables (two join statements)

The script first preprocesses the data (null removal, outlier removal, and duplicate checking) using
the in-house functions in the file sql.preprocessing from this same directory. Then, the aggregation
tasks are run.

Each task is executed 100 times (n=100), and for each execution, the execution time, CPU time, and CPU
percentage are recorded. The results are exported to CSV files for further analysis.

Given that SQL does not make use of multi-core parallelism, the overall CPU percentage is recorded.

There are several print statements that have been commented out. These were used for checking the
correctness of the program. I have left these to show some of the process of creating this file.

Sources:
- https://www.postgresql.org/docs/current/tutorial-join.html
- https://www.postgresql.org/docs/current/functions-datetime.html#FUNCTIONS-DATETIME-EXTRACT
- https://docs.python.org/3/library/csv.html
"""

import psycopg2
from psycopg2 import sql
import metrics
import csv
import sql_preprocessing as sp

n = 100

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESS

conn = sp.conn
cur = conn.cursor()

sp.load_data(conn)
sp.remove_nulls(conn)
sp.remove_outliers(conn)
sp.check_duplicates(conn)

# print("Row counts AFTER preprocessing:")
sp.row_counts(conn)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 1: Single table aggregation tasks

# Single table 1

def single_table_1():
    """
    Groups patients by gender.
    """

    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT gender, COUNT(*)
        FROM patients
        GROUP BY gender
    """)
    result = cur.fetchall()

    # for result in result1:
        # print(result)

    print(f"Number of patients grouped by gender: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU time: {cpu_time}")

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Single table 2
def single_table_2():
    """
    Groups number of surgeries by surgery type.
    """

    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT surgery_type, COUNT(*)
        FROM surgeryrecord
        GROUP BY surgery_type
    """)
    # print("\n")
    result = cur.fetchall()
    
    # for result in result2:
        # print(result)

    print(f"Number of surgeries grouped by surgery type: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU time: {cpu_time}")

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Results
time_rows_single = []
cpu_percent_rows_single = []
cpu_time_rows_single = []

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_1()
    time_rows_single.append(["patients_by_gender", i, elapsed])
    cpu_percent_rows_single.append(["patients_by_gender", i, cpu_percent])
    cpu_time_rows_single.append(["patients_by_gender", i, cpu_time])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_2()
    time_rows_single.append(["surgeries_by_type", i, elapsed])
    cpu_percent_rows_single.append(["surgeries_by_type", i, cpu_percent])
    cpu_time_rows_single.append(["surgeries_by_type", i, cpu_time])

# Creating .csv files
f = open("single_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_ms"])
writer.writerows(time_rows_single)
f.close()

f = open("single_cpu_percent_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_single)
f.close()

f = open("single_cpu_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_time_ms"])
writer.writerows(cpu_time_rows_single)
f.close()

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 2: Two-table aggregation tasks

# Two-table 1
def two_table_1():
    """
    Number of doctors per department.
    """
    
    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT dept_name, COUNT(*)
        FROM doctor
        INNER JOIN department ON doctor.dept_id = department.dept_id
        GROUP BY dept_name
    """)
    result = cur.fetchall()

    print(f"Number of doctors per department: {len(result)}")
    
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Two-table 2
def two_table_2():
    """
    Number of appointments per patient.
    """
    
    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT patients.patient_id, fname, lname, COUNT(*)
        FROM appointment
        INNER JOIN patients ON appointment.patient_id = patients.patient_id
        GROUP BY patients.patient_id, fname, lname
    """)
    result = cur.fetchall()

    print(f"Number of appointments per patient: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Saving results
time_rows_two = []
cpu_percent_rows_two = []
cpu_time_rows_two = []

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = two_table_1()
    time_rows_two.append(["doctors_per_dept", i, elapsed])
    cpu_percent_rows_two.append(["doctors_per_dept", i, cpu_percent])
    cpu_time_rows_two.append(["doctors_per_dept", i, cpu_time])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = two_table_2()
    time_rows_two.append(["appointments_per_patient", i, elapsed])
    cpu_percent_rows_two.append(["appointments_per_patient", i, cpu_percent])
    cpu_time_rows_two.append(["appointments_per_patient", i, cpu_time])

f = open("two_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_ms"])
writer.writerows(time_rows_two)
f.close()

f = open("two_cpu_percent_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_two)
f.close()

f = open("two_cpu_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_time_ms"])
writer.writerows(cpu_time_rows_two)
f.close()


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 3: Multi-table (three-or-more) aggregation tasks

# Three-table 1
def three_table_1():
    """
    Number of surgeries per department per month.
    """
    
    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT dept_name, EXTRACT(MONTH FROM surgery_date), COUNT(*)
        FROM surgeryrecord
        INNER JOIN doctor ON surgeryrecord.surgeon_id = doctor.doct_id
        INNER JOIN department ON doctor.dept_id = department.dept_id
        GROUP BY dept_name, EXTRACT(MONTH FROM surgery_date)
    """)
    result = cur.fetchall()

    print(f"Number of surgeries per department per month: {len(result)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Three-table 2
def three_table_2():
    """
    Number of appointments per doctor per department.
    """
    
    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT dept_name, doctor.doct_id, doctor.fname, doctor.lname, COUNT(*)
        FROM appointment
        INNER JOIN doctor ON appointment.doct_id = doctor.doct_id
        INNER JOIN department ON doctor.dept_id = department.dept_id
        GROUP BY dept_name, doctor.doct_id, doctor.fname, doctor.lname
    """)
    result = cur.fetchall()

    print(f"Number of appointments per doctor per department: {len(result)}")
    
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Saving results
time_rows_three = []
cpu_percent_rows_three = []
cpu_time_rows_three = []

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = three_table_1()
    time_rows_three.append(["surgeries_per_dept_per_month", i, elapsed])
    cpu_percent_rows_three.append(["surgeries_per_dept_per_month", i, cpu_percent])
    cpu_time_rows_three.append(["surgeries_per_dept_per_month", i, cpu_time])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = three_table_2()
    time_rows_three.append(["appointments_per_doctor_per_dept", i, elapsed])
    cpu_percent_rows_three.append(["appointments_per_doctor_per_dept", i, cpu_percent])
    cpu_time_rows_three.append(["appointments_per_doctor_per_dept", i, cpu_time])

f = open("three_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_ms"])
writer.writerows(time_rows_three)
f.close()

f = open("three_cpu_percent_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_three)
f.close()

f = open("three_cpu_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_time_ms"])
writer.writerows(cpu_time_rows_three)
f.close()

# Closing cursor and connection
cur.close()
conn.close()


