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
    """

    # Creating the dataframes from each sheet in the excel file
    dataframes = {}

    for sheet in tables:
        dataframes[sheet] = pl.read_excel(excel, sheet_name=sheet)

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
    total_count = 0

    for sheet, df in dataframes.items():
        count = len(df)
        total_count += count
        
        # print(f" {sheet}: {count} rows")

    print(f" Total row count: {total_count}")

