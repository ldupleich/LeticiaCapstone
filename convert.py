import re
import os

INPUT_PATH  = "archive/Hospital_Management_System.sql"
OUTPUT_PATH = "archive/Hospital_Management_System_postgres.sql"

# Drop tables in reverse dependency order before recreating them
# With this, we can rerun this file without errors that the tables already exist
DROP_TABLES = """\
DROP TABLE IF EXISTS SurgeryRecord CASCADE;
DROP TABLE IF EXISTS StaffShift CASCADE;
DROP TABLE IF EXISTS MedicalRecord CASCADE;
DROP TABLE IF EXISTS Appointment CASCADE;
DROP TABLE IF EXISTS RoomRecords CASCADE;
DROP TABLE IF EXISTS BedRecords CASCADE;
DROP TABLE IF EXISTS Patients CASCADE;
DROP TABLE IF EXISTS Bed CASCADE;
DROP TABLE IF EXISTS Ward CASCADE;
DROP TABLE IF EXISTS Helpers CASCADE;
DROP TABLE IF EXISTS Nurse CASCADE;
DROP TABLE IF EXISTS Doctor CASCADE;
DROP TABLE IF EXISTS Room CASCADE;
DROP TABLE IF EXISTS Department CASCADE;
"""

# REGEX NOTES
# always start with ^ and end with $ for T-SQL statements
# multiline to go across each line
# ^\s* -> leading whitespace
# USE\s+ -> space after keyword
# \S+ -> any non whitespace (the db/table name)
# \s*;?\s*$ -> optional whitespace, optional semicolon, end of line
# r");\1\2" -> to put stuff back


def convert_sql_postgres(sql):

    # Strip UTF-8 BOM
    sql = sql.lstrip("\ufeff")

    # Remove block comments /* ... */
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)

    # Remove single-line comments -- ...
    sql = re.sub(r"--[^\n]*", "", sql)

    # Remove T-SQL-only statements with no PostgreSQL equivalent
    sql = re.sub(r"^\s*GO\s*$", "", sql, flags=re.MULTILINE | re.IGNORECASE)
    sql = re.sub(r"^\s*USE\s+\S+\s*;?\s*$", "", sql, flags=re.MULTILINE | re.IGNORECASE)
    sql = re.sub(r"^\s*CREATE\s+DATABASE\s+\S+\s*;?\s*$", "", sql, flags=re.MULTILINE | re.IGNORECASE)

    # Fix INSERT blocks where a semicolon is missing from the last row
    sql = re.sub(r"\)(\s+)(Insert\s+Into)", r");\1\2", sql, flags=re.IGNORECASE)

    # Delete existing tables so no error happens
    sql = DROP_TABLES + sql

    return sql

# Input file
with open(INPUT_PATH, "r", encoding="utf-8-sig") as f:
    raw = f.read()

clean = convert_sql_postgres(raw)

# Output file (make a new directory)
os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(clean)

print(f"Data has been converted.")
