# SQL vs Polars: Measuring CPU Utilization and Execution Time for Aggregation Tasks on Relational Healthcare Data

## General Details
- Author (AUC): Leticia Dupleich Smith (Email: leticia.dupleich.smith@student.uva.nl)
- Author’s Student Number: 15048748
- Supervisor (AUC): dr. Luis Aguilar Suarez (Email: l.e.aguilarsuarez@auc.nl)
- Reader (AUC): dr. Chris Jones (Email: c.jones@auc.nl)
- Tutor (AUC): dr. Luis Aguilar Suarez (Email: l.e.aguilarsuarez@auc.nl)
- Major: Sciences

## Abstract
The rapid growth of data has made efficient data management increasingly important, particularly in healthcare systems where 
hospitals generate large volumes of relational clinical and administrative data daily. While Structured Query Language (SQL) 
is the standard tool for managing and querying relational databases, its computational efficiency for complex aggregation 
tasks has been identified as a possible limitation as dataset sizes grow. Polars, a Python-based DataFrame library, has emerged 
as a potentially more efficient alternative due to its use of multi-core parallelism and query optimization. However, limited 
comparative research currently exists between the two tools, which is an important literary gap given that hospitals rely on 
fast and efficient data processing for clinical tasks, such as retrieving patient histories, monitoring treatment outcomes, 
and managing staff. This study addresses this gap by investigating differences in Central Processing Unit (CPU) utilization 
and execution time between SQL and Polars when performing equivalent aggregation tasks of varying complexity on a real-world 
hospital management dataset. In this way, this research aims to determine which tool is better suited for data-intensive 
healthcare environments. Six aggregation tasks are designed, ranging from single-table operations to multi-table operations. 
Results are expected to show that Polars will exhibit higher CPU utilization than SQL due to its multi-core architecture and 
shorter execution times due to its parallel processing. However, it is yet to be determined whether this difference will persist 
as relational complexity increases. 

## Files
`archive`

`convert.py`

`metrics.py`

`polars_analysis.py`

`sql_analysis.py`

`single_time_polars.py`

`single_time_sql.py`

`single_time_overall.py`
