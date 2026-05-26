# SQL vs Polars: Measuring CPU Utilization and Execution Time for Aggregation Tasks on Relational Healthcare Data

## General Details
- Author (AUC): Leticia Dupleich Smith (Email: leticia.dupleich.smith@student.uva.nl)
- Author’s Student Number: 15048748
- Supervisor (AUC): dr. Luis Aguilar Suarez (Email: l.e.aguilarsuarez@auc.nl)
- Reader (AUC): dr. Chris Jones (Email: c.jones@auc.nl)
- Tutor (AUC): dr. Luis Aguilar Suarez (Email: l.e.aguilarsuarez@auc.nl)
- Major: Sciences

## Abstract
The rapid growth of data has made efficient data management increasingly important, particularly in healthcare systems where hospitals generate large volumes of relational clinical and administrative data daily. While Structured Query Language (SQL) is the standard tool for managing and querying relational databases, its computational efficiency for complex aggregation tasks has been identified as a possible limitation as dataset sizes grow. Polars, a Python-based DataFrame library, has emerged as a potentially more efficient alternative due to its use of multi-core parallelism and query optimization. However, limited comparative research currently exists between the two tools, which is an important literary gap given that hospitals rely on fast and efficient data processing for clinical tasks, such as retrieving patient histories, monitoring treatment outcomes, and managing staff. This study addresses this gap by investigating differences in Central Processing Unit (CPU) utilization and execution time between SQL and Polars when performing equivalent aggregation tasks of varying complexity on a real-world hospital management dataset. In this way, this research aims to determine which tool is better suited for data-intensive healthcare environments. Six aggregation tasks are designed, ranging from single-table operations to multi-table operations. Results are expected to show that Polars will exhibit higher CPU utilization than SQL due to its multi-core architecture and shorter execution times due to its parallel processing. However, it is yet to be determined whether this difference will persist as relational complexity increases. 

## Files
- `archive`: The folder that contained the dataset provided by Kaggle. In this folder, you can find a visual depiction of the relational database as well as both the SQL and Excel datasets.

- `convert.py`: This Python script is used to convert from T-SQL to PostgreSQL. It takes the original SQL dataset "Hospital_Management_System.sql" in the archive folder and outputs "Hospital_Management_System_postgres.sql" also to the archive folder.

- `metrics.py`: In this Python script you can find the functions used to obtain the time execution, CPU per core percent, CPU total percent, and CPU time metrics.

- `polars_analysis.py` and `sql_analysis.py`: These files contain the entire preprocessing pipelines for Polars and SQL as well as the single-table aggregation tasks at the bottom of the file.

- `single_time_polars.csv`, `single_cpu_polars.csv`, `single_cpu_time_polars.csv`: Each of these files contains the raw data obtained from executing the single-table aggregation tasks for Polars.

- `single_time_sql.csv`, `single_cpu_sql.csv`, `single_cpu_time_sql.csv`: Each of these files contains the raw data obtained from executing the single-table aggregation tasks for SQL.

- `results.xlsx`: Given that the raw data is obtained in a .csv file, the comma separators place all the data into one column. In this file, there are several tabs for each of the raw data files, where the data is split into three columns and the average and standard deviation is calculated for each task. There are also three tabs for the different metrics where the averages and standard deviations are used to plot the results. During the meetings, a scatter plot was brought forth as the preferred plotting method; however, I thought that the bar chart perhaps better visually displays the differences between SQL and Polars for the two tasks.
