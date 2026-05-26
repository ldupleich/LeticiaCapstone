# Results for Single-Table Aggregation Tasks

This folder contains all the results from the single-table aggregation tasks, including raw results and processed ones where processed refers to neat Excel tables and graphs.

## Excel File

`results_single`: This excel sheet contains the processed results obtained from running all the single-table aggregation tasks. It has multiple tabs that contain different types of information:

**Polars Specific:** These sheets contain the processed raw data from the single-table aggregation tasks using Polars for both tasks (one after the other), and a table with average and standard deviations for the data.
- time_polars
- cpu_percent_polars
- cpu_time_polars

**SQL Specific:** These sheets contain the processed raw data from the single-table aggregation tasks using SQL for both tasks (one after the other), and a table with average and standard deviations for the data.
- time_sql
- cpu_percent_sql
- cpu_time_sql
  
**Comparison Results:** These sheets contain the final average and standard deviation tables for both single-table aggregation tasks using both tools (Polars and SQL), as well as a bar chart and a line chart comparing the results.
- time_overall 
- cpu_percent_overall
- cpu_time_overall
  
**Additional:** This sheet contains four tables where each of them is a comparison between the execution time and CPU time of a specific task using either Polars or SQL. These are graphed to check for differences and trends.
- cpu_time_vs_elapsed

## CSV Files
`single_cpu_percent_polars.csv`, `single_cpu_percent_sql.csv`, `single_cpu_time_polars.csv`, `single_cpu_time_sql`, `single_time_polars`, `single_time_sql`: All of these files are the outputs of the aggregation tasks where the metrics are recorded. These csv files are not processed or edited, they are the raw results.
