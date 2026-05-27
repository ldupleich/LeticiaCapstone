"""
This script is responsible for the preprocessing of the SQL Hopsital Management Dataset
so that they can be used in the aggregation tasks.

The main steps necessary are:
    1. Load the data from the SQL file
    2. Remove any NULLs only if they appear in the dictionary
    3. Remove outliers (only numerical columns)
    4. Check for duplicate rows and remove if necessary (keep smallest primary key)
    5. Print row count (used to compare with Polars)

There are many additional checks within each function, and these were added as the code was
being developed and errors were thrown.

This file is imported and called prior to performing the aggregation tasks in "sql_aggregation".
This means that this file does not have to be run independently, it will be run automatically when
"sql_aggregation" is ran.

Sources:
- https://www.geeksforgeeks.org/sql/what-is-cursor-in-sql/
- https://www.postgresql.org/docs/current/functions-conditional.html
- https://www.w3schools.com/sql/sql_null_values.asp
- https://www.geeksforgeeks.org/sql/sql-query-to-delete-duplicate-rows/
- https://www.w3schools.com/sql/sql_delete.asp
- https://www.postgresql.org/docs/9.4/functions-aggregate.html
"""

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
    """
    Loads the Hospital Management Dataset into a PostgreSQL dataset.
    """
    
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
    """
    Prints the remaining number of rows after preprocessing to compare with Polars.
    The per-row count is also present but commented out.
    """
    
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
    print(f"Total row count: {total_count}")


