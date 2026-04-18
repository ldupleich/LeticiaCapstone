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
# PREPROCESSING 5: Print row count to compare with Polars

def row_counts(dataframes):
    total_count = 0

    for sheet, df in dataframes.items():
        count = len(df)
        total_count += count
        
        # print(f" {sheet}: {count} rows")

    # print("\n")
    print(f" Total: {total_count}")

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PREPROCESSING 6: Print counts before and after to see how much was changed

dataframes = load_data()

# print("\n")
# print("Row counts BEFORE preprocessing:")

# for sheet, df in dataframes.items():
    # print(f" {sheet}: {len(df)} rows")

dataframes = remove_nulls(dataframes)
dataframes = remove_outliers(dataframes)
dataframes = check_duplicates(dataframes)

# print("\n")
# print("Row counts AFTER preprocessing:")
row_counts(dataframes)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AGGREGATION 1: Single table aggregation tasks

print("\n")
print("SINGLE TABLE AGGREGATION:")

# Single table 1
def single_table_1(dataframes):
    """Groups patients by gender."""
    start_time = metrics.start()

    result1 = (
        dataframes["Patients"]
        .lazy() # recommended instead of eager
        .group_by("Gender")
        .agg(pl.len())
    )
    print(result1.collect())
    print(f"Number of patients grouped by gender: {len(result1.collect())}")

    elapsed, cpu_per_core, cpu_process = metrics.stop(start_time)
    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU usage per core: {cpu_per_core}")
    # print(f" CPU usage: {cpu_process}")

    return elapsed, cpu_per_core, cpu_process

# Single table 2
def single_table_2(dataframes):
    """Groups number of surgeries by surgery type."""
    start_time = metrics.start()

    result2 = (
        dataframes["SurgeryRecord"]
        .lazy() # recommended instead of eager
        .group_by("surgery_Type")
        .agg(pl.len())
    )
    print("\n")
    print(result2.collect())
    print(f"Number of surgeries grouped by surgery type: {len(result2.collect())}")
    
    elapsed, cpu_per_core, cpu_process = metrics.stop(start_time)
    # print(f" Execution time: {elapsed:.4f}s")
    # print(f" CPU usage per core: {cpu_per_core}")
    # print(f" CPU usage: {cpu_process}")

    return elapsed, cpu_per_core, cpu_process

# Saving results
n = 100
time_rows = []

for i in range(n):
    elapsed, cpu_per_core, cpu_process = single_table_1(dataframes)
    time_rows.append(["patients_by_gender", i, elapsed])

for i in range(n):
    elapsed, cpu_per_core, cpu_process = single_table_2(dataframes)
    time_rows.append(["surgeries_by_type", i, elapsed])

f = open("single_time_polars.csv", "w", newline="")
writer = csv.writer(f)
writer.writerow(["query", "trial", "elapsed_s"])
writer.writerows(time_rows)
f.close()
    



