# SQL vs Polars: CPU Utilization and Execution Time Benchmarking on Relational Healthcare Data

## General Details
- Author: Leticia Dupleich Smith (student number 15048748), Amsterdam University College, leticia.dupleich.smith@student.uva.nl
- Supervisor: dr. Luis Aguilar Suarez (AUC), l.e.aguilarsuarez@auc.nl
- Reader: dr. Chris Jones (AUC), c.jones@auc.nl
- Tutor: dr. Luis Aguilar Suarez (AUC), l.e.aguilarsuarez@auc.nl)
- Major: Sciences
- Date of submission: 27 May 2026

## Abstract
The rapid growth of data has made efficient data management increasingly important, particularly in healthcare systems where hospitals generate large volumes of relational clinical and administrative data daily. While Structured Query Language (SQL) is the standard tool for managing and querying relational databases, its computational efficiency for complex aggregation tasks has been identified as a possible limitation as dataset sizes grow. In contrast, Polars, a Python-based DataFrame library, has emerged as a potentially more efficient alternative due to its use of multi-core parallelism and query optimization. However, limited comparative research currently exists between these two tools, which is an important literary gap given that hospitals rely on fast and efficient data processing for clinical tasks, such as retrieving patient histories, monitoring treatment outcomes, and managing staff. This study addresses this gap by investigating differences in Central Processing Unit (CPU) utilization and execution time between SQL and Polars when performing equivalent aggregation tasks of varying complexity on a real-world hospital management dataset. Results show that SQL outperformed Polars in execution time for all single-table aggregation tasks, while Polars demonstrated faster runtimes for certain multi-table queries, suggesting its parallelism may become more beneficial as workload complexity increases. Polars consistently exhibited higher per-core CPU utilization than SQL, but this likely reflects its multi-core architecture rather than resource inefficiency. Neither tool was found to consistently outperform the other across all conditions, suggesting that the optimal choice in a hospital management context depends on the specific characteristics of the query.

## Database
<img width="1304" height="1081" alt="image" src="https://github.com/user-attachments/assets/ac2a3eba-2530-4878-869c-04bbc99bac1f" />

## Aggregation Tasks
Single-table
- Patients grouped by gender
- Surgeries grouped by type

Two-table
- Doctors grouped by department
- Appointments grouped by patient

Three-table
- Surgeries grouped by department grouped by month
- Appointments grouped by doctor grouped by department

## File Descriptions
- `archive`: The folder that contained the dataset provided by Kaggle. In this folder, you can find both the SQL and Excel datasets.

- `convert.py`: This Python script is used to convert from T-SQL to PostgreSQL. It takes the original SQL dataset "Hospital_Management_System.sql" in the archive folder and outputs "Hospital_Management_System_postgres.sql" also to the archive folder.

- `metrics.py`: In this Python script you can find the functions used to obtain the time execution, CPU per core percent, CPU total percent, and CPU time metrics.

- `polars_preprocessing`, `sql_preprocessing`: These Python scripts contain the entire preprocessing pipeline for Polars and SQL.
  
- `polars_aggregation`, `sql_aggregation`: These Python scripts contain the aggregation tasks that will be tested, as well as the code to save these into CSV files (these were moved into the result folders).

- `results_single`, `results_two`, `results_three`: These folders contain all of the results obtained throughout the study.

## Running the Code
1. Clone the repository.
2. Run `convert.py`
3. Run `polars_aggregation.py`
4. Run `sql_aggregation.py`
