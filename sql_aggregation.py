import psycopg2
from psycopg2 import sql
import metrics
import csv
import sql_preprocessing as sp

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESS

conn = sp.conn
cur = conn.cursor()

sp.load_data(conn)
sp.remove_nulls(conn)
sp.remove_outliers(conn)
sp.check_duplicates(conn)

# print("\n")
# print("Row counts AFTER preprocessing:")
sp.row_counts(conn)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 1: Single table aggregation tasks

# Single table 1

def single_table_1():
    """Groups patients by gender."""

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
    """Groups number of surgeries by surgery type."""

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
n = 100
time_rows_single = []
cpu_percent_rows_single = []

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_1()
    time_rows_single.append(["patients_by_gender", i, elapsed])
    cpu_percent_rows_single.append(["patients_by_gender", i, cpu_percent])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_2()
    time_rows_single.append(["surgeries_by_type", i, elapsed])
    cpu_percent_rows_single.append(["surgeries_by_type", i, cpu_percent])

# Creating .csv files
f = open("single_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_s"])
writer.writerows(time_rows_single)
f.close()

f = open("single_cpu_percent_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_single)
f.close()

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 2: Multi-table aggregation tasks

# Multi-table 1
def two_table_1():
    """Number of doctors per department."""
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

# Multi-table 2
def two_table_2():
    """Number of appointments per patient."""
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

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = two_table_1()
    time_rows_two.append(["doctors_per_dept", i, elapsed])
    cpu_percent_rows_two.append(["doctors_per_dept", i, cpu_percent])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = two_table_2()
    time_rows_two.append(["appointments_per_patient", i, elapsed])
    cpu_percent_rows_two.append(["appointments_per_patient", i, cpu_percent])

f = open("two_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_s"])
writer.writerows(time_rows_two)
f.close()

f = open("two_cpu_percent_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_two)
f.close()

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 3: Multi-table (three-or-more) aggregation tasks

# Three-table 1
def three_table_1():
    """Number of surgeries per department per month."""
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
    """Number of appointments per doctor per department."""
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

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = three_table_1()
    time_rows_three.append(["surgeries_per_dept_per_month", i, elapsed])
    cpu_percent_rows_three.append(["surgeries_per_dept_per_month", i, cpu_percent])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = three_table_2()
    time_rows_three.append(["appointments_per_doctor_per_dept", i, elapsed])
    cpu_percent_rows_three.append(["appointments_per_doctor_per_dept", i, cpu_percent])

f = open("three_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_s"])
writer.writerows(time_rows_three)
f.close()

f = open("three_cpu_percent_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows_three)
f.close()

# Closing cursor and connection
cur.close()
conn.close()


