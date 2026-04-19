import psycopg2
from psycopg2 import sql
import metrics
import csv

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# CUSOR AND CONNECTION

# Connect to default postgres database
conn = psycopg2.connect("dbname=postgres user=leticiadupleich host=localhost")
conn.autocommit = True  # needed for CREATE DATABASE
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = 'hospital_database'")

if not cur.fetchone():
    cur.execute("CREATE DATABASE hospital_database")

conn.close()

# Now connect to the new database
conn = psycopg2.connect("dbname=hospital_database user=leticiadupleich host=localhost")
conn.autocommit = False

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TABLES AND RESTRICTIONS

# Dictionary of tables and their primary keys for looping in later functions
tables = {
    "department":    "dept_id",
    "doctor":        "doct_id",
    "patients":      "patient_id",
    "appointment":   "appointment_id",
    "medicalrecord": "record_id",
    "surgeryrecord": "surgery_id",
}

# Columns that should never be NULL
not_null = {
    "department":    ["dept_id", "dept_name"],
    "doctor":        ["doct_id", "dept_id", "fname", "lname"],
    "patients":      ["patient_id", "fname", "lname", "gender", "date_of_birth"],
    "appointment":   ["appointment_id", "patient_id", "doct_id", "appointment_date"],
    "medicalrecord": ["record_id", "doct_id", "patient_id", "visit_date"],
    "surgeryrecord": ["surgery_id", "patient_id", "surgeon_id", "surgery_date", "surgery_type"],
}

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 1: Load data from sql file

def load_data(conn):
    cur = conn.cursor() # open cursor
 
    with open("archive/Hospital_Management_System_postgres.sql", "r", encoding="utf-8-sig") as f:
        sql_file = f.read()
 
    cur.execute(sql_file)
 
    conn.commit() # manual commit
    cur.close() # close cursor
    # print("Data loaded successfully")

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 2: Detect and remove NULLs

def remove_nulls(conn):
    """
    Scans all the values in all the loaded tables and removes NULL values.
    """
    cur = conn.cursor()
 
    for table, columns in not_null.items():
        for column in columns:
            cur.execute(sql.SQL("""
                DELETE FROM {} WHERE {} IS NULL
            """).format(
                sql.Identifier(table),
                sql.Identifier(column)
            ))
 
    conn.commit()
    cur.close()
    # print("NULL values removed successfully")

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 3: Detect and remove outliers (numerical)

def remove_outliers(conn):
    """
    Scans all the numerical values in the loaded tables and removes outliers.
    """
    
    cur = conn.cursor() # open cursor

    for table, primary_key in tables.items():
        
        # Selecting numeric columns
        cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s
                AND column_name != %s
                AND data_type IN ('integer', 'numeric', 'decimal', 'real', 'double precision', 'bigint', 'smallint')
        """, (table, primary_key))

        numeric_columns = [row[0] for row in cur.fetchall()]

        # Calculate percentiles for each column for bounds
        for column in numeric_columns:
            cur.execute(sql.SQL("""
                SELECT
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {}),
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {})
                FROM {}
            """).format(
                sql.Identifier(column),
                sql.Identifier(column),
                sql.Identifier(table)
            ))

            result = cur.fetchone()

            if result is None or result[0] is None:
                continue
            
            q1 = result[0]
            q3 = result[1]

            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Remove rows that do not fit the bounds
            cur.execute(sql.SQL("""
                DELETE FROM {} WHERE {} < %s OR {} > %s
            """).format(
                sql.Identifier(table),
                sql.Identifier(column),
                sql.Identifier(column)
            ), (lower_bound, upper_bound))

    conn.commit() # manual commit
    cur.close() # close cursor
    # print("Outliers removed successfully")

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 4: Verify duplicate rows

def check_duplicates(conn):
    """
    Checks whether there are duplicate rows and removes them in the case that there are.
    """

    cur = conn.cursor() # open cursor

    # We only want to check the columns that are not primary key
    # Primary key is SUPPOSED to be unique
    for table, primary_key in tables.items():
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            AND column_name != %s
        """, (table, primary_key))

        other_columns = [row[0] for row in cur.fetchall()]

        cur.execute(sql.SQL("""
            DELETE FROM {}
            WHERE {} NOT IN (
                SELECT MIN({})
                FROM {}
                GROUP BY {}
            )
        """).format(
            sql.Identifier(table),
            sql.Identifier(primary_key),
            sql.Identifier(primary_key),
            sql.Identifier(table),
            sql.SQL(", ").join(sql.Identifier(col) for col in other_columns)
        ))

    conn.commit() # manual commit
    cur.close() # close cursor
    # print("Duplicates verified successfully")

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 5: Print row count to compare with Polars

def row_counts(conn):
    cur = conn.cursor() # open cursor

    total_count = 0
    
    for table in tables:
        cur.execute(sql.SQL("""
            SELECT COUNT(*) FROM {}
        """).format(
            sql.Identifier(table)
        ))

        result = cur.fetchone()
        count = result[0]
        total_count += count

        # print(f" {table}: {count} rows")

    cur.close() # close cursor
    # print("\n")
    print(f"Total number of rows in file: {total_count}")

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 6: Print counts before and after to see how much was changed
cur = conn.cursor()

load_data(conn)


# print("\n")
# print("Row counts BEFORE preprocessing:")
for table in tables:
    cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
    # print(f" {table}: {cur.fetchone()[0]} rows")

remove_nulls(conn)
remove_outliers(conn)
check_duplicates(conn)
cur.close()

# print("\n")
# print("Row counts AFTER preprocessing:")
row_counts(conn)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 1: Single table aggregation tasks

# print("\n")
# print("SINGLE TABLE AGGREGATION:")

cur = conn.cursor()

# Single table 1
def single_table_1():
    """Groups patients by gender."""

    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT gender, COUNT(*) AS total_patients
        FROM patients
        GROUP BY gender
    """)
    result1 = cur.fetchall()

    # for result in result1:
        # print(result)
    # print(f" Total number of patients grouped by gender: {len(result1)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU time: {cpu_time}")

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Single table 2
def single_table_2():
    """Groups number of surgeries by surgery type."""

    start_time, process_before = metrics.start()

    cur.execute("""
        SELECT surgery_type, COUNT(*) AS total_surgeries
        FROM surgeryrecord
        GROUP BY surgery_type
    """)
    # print("\n")
    result2 = cur.fetchall()
    
    # for result in result2:
        # print(result)
    # print(f" Number of surgeries grouped by surgery type: {len(result2)}")

    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = metrics.stop(start_time, process_before)
    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU time: {cpu_time}")

    return elapsed, cpu_time, cpu_percent_per_core, cpu_percent

# Results
n = 100
time_rows = []
cpu_time_rows = []
cpu_percent_rows = []

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_1()
    time_rows.append(["patients_by_gender", i, elapsed])
    cpu_time_rows.append(["patients_by_gender", i, cpu_time])
    cpu_percent_rows.append(["patients_by_gender", i, cpu_percent])

for i in range(n):
    elapsed, cpu_time, cpu_percent_per_core, cpu_percent = single_table_2()
    time_rows.append(["surgeries_by_type", i, elapsed])
    cpu_time_rows.append(["surgeries_by_type", i, cpu_time])
    cpu_percent_rows.append(["surgeries_by_type", i, cpu_percent])

# Creating .csv files
f = open("single_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_s"])
writer.writerows(time_rows)
f.close()

f = open("single_cpu_time_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_time_s"])
writer.writerows(cpu_time_rows)
f.close()

f = open("single_cpu_percent_sql.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "cpu_percent"])
writer.writerows(cpu_percent_rows)
f.close()

# Closing cursor and connection
cur.close()
conn.close()


