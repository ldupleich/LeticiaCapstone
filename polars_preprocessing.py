"""
This script is responsible for the preprocessing of the Hopsital Management Dataset
from Excel into Polars dataframes that can be used in the aggregation tasks.

The main steps necessary are:
    1. Load the data from Excel
    2. Remove any NULLs only if they appear in the dictionary
    3. Remove outliers (only numerical columns)
    4. Check for duplicate rows and remove if necessary (keep smallest primary key)
    5. Print row count (used to compare with SQL)

There are many additional checks within each function, and these were added as the code was
being developed and errors were thrown.

This file is imported and called prior to performing the aggregation tasks in "polars_aggregation".
This means that this file does not have to be run independently, it will be run automatically when
"polars_aggregation" is ran.

Sources:
- https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.drop_nulls.html
- https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.quantile.html
- https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.filter.html
- https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.unique.html
- https://www.geeksforgeeks.org/python/how-to-drop-row-in-polars-python/
- https://www.geeksforgeeks.org/sql/sql-query-to-delete-duplicate-rows/
- https://claude.ai/share/dc96d131-dbc5-4552-8307-6ac36a2e8e96
"""

import polars as pl
import metrics
import psutil
import csv

excel = "archive/Hospital Management System.xlsx"

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TABLES AND RESTRICTIONS

# Dictionary of sheet names and their primary keys
tables = {
    "Department":    "dept_Id",
    "Doctor":        "doct_Id",
    "Patients":      "patient_Id",
    "Appointment":   "appoIntment_Id",
    "MedicalRecord": "record_Id",
    "SurgeryRecord": "surgery_Id",
}
 
# Columns that should never be NULL
not_null = {
    "Department":    ["dept_Id", "dept_Name"],
    "Doctor":        ["doct_Id", "dept_Id", "FName", "LName"],
    "Patients":      ["patient_Id", "FName", "LName", "Gender", "Date_Of_Birth"],
    "Appointment":   ["appoIntment_Id", "patient_Id", "doct_Id", "appointment_Date"],
    "MedicalRecord": ["record_Id", "doct_Id", "patient_Id", "visit_Date"],
    "SurgeryRecord": ["surgery_Id", "patient_Id", "surgeon_Id", "surgery_Date"],
}

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING: Load data from Excel

def load_data():
    """
    Reads all sheets from the Excel file into a dict of Polars DataFrames.
    The additional checks (e.g. round float columns) were inserted to make
    the loading of the data more similar to SQL.
    """

    # Creating the dataframes from each sheet in the excel file
    dataframes = {}

    for sheet in tables:
        df = pl.read_excel(excel, sheet_name=sheet)

        # Round float columns to 2 decimal places
        for col in df.columns:
            if df[col].dtype in (pl.Float32, pl.Float64):
                df = df.with_columns(pl.col(col).round(2))

        # Fix time-only columns stored as dummy datetimes by Excel
        for col in ["start_time", "end_time"]:
            if col in df.columns:
                df = df.with_columns(pl.col(col).dt.time())

        dataframes[sheet] = df

    # print("Data loaded successfully")
    return dataframes

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 2: Detect and remove NULLs

def remove_nulls(dataframes):
    """
    Scans all the values in all the loaded tables and removes NULL values.
    """

    # Drop nulls only of the columns that are specified as not null
    for sheet, columns in not_null.items():
        dataframes[sheet] = dataframes[sheet].drop_nulls(subset=columns)

    # print("NULL values removed successfully")
    return dataframes

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 3: Detect and remove outliers (numerical)

def remove_outliers(dataframes):
    """
    Scans all the numerical values in the loaded tables and removes outliers.
    """

    numeric_types = (
        pl.Int8, pl.Int16, pl.Int32, pl.Int64,
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        pl.Float32, pl.Float64, pl.Decimal,
    )
    
    # Was causing an error since office number was being counted as numerical
    exclude_from_outliers = {
        "Doctor": ["dept_Id", "office_No"],
    }

    for sheet, primary_key in tables.items():
        df = dataframes[sheet]

        # Identify numeric columns, excluding the primary key
        exclude = {primary_key} | set(exclude_from_outliers.get(sheet, []))

        numeric_columns = []
        for column in df.columns:
            if column not in exclude and df[column].dtype in numeric_types:
                numeric_columns.append(column)

        # Calculate IQR for every numeric column
        for column in numeric_columns:
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)

            if q1 is None or q3 is None:
                continue

            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Remove rows outside the IQR
            df = df.filter(
                (df[column] >= q1 - 1.5 * iqr) & (df[column] <= q3 + 1.5 * iqr)
            )

        dataframes[sheet] = df

    # print("Outliers removed successfully")
    return dataframes

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 4: Verify duplicate rows

def check_duplicates(dataframes):
    """
    Checks whether there are duplicate rows and removes them in the case that there are.
    """

    for sheet, primary_key in tables.items():
        df = dataframes[sheet]

        # We only want to check the columns that are not primary key
        other_columns = []
        for col in df.columns:
            if col != primary_key:
                other_columns.append(col)

       # Remove duplicates
        dataframes[sheet] = df.unique(subset=other_columns)

    # print("Duplicates verified successfully")
    return dataframes

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 5: Print row count to compare with sql

def row_counts(dataframes):
    """
    Prints the remaining number of rows after preprocessing to compare with SQL.
    The per-row count is also present but commented out.
    """
    total_count = 0

    for sheet, df in dataframes.items():
        count = len(df)
        total_count += count
        
        # print(f" {sheet}: {count} rows")

    print(f" Total row count: {total_count}")

