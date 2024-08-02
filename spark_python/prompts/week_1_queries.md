## Week 1 Queries and Solutions

### Query 1: Actors Table DDL

**Assignment Prompt:** 
> Write a DDL query to create the `actors` table.

**Example solution:**
```sql
```

### Query 2: Cumulative Table Computation Query
This query populates the actors table by combining data from two different years.

**Assignment Prompt:** 
> Write a query that populates the `actors` table one year at a time.

**Example solution:**
```sql
```
### Query 3: Actors History SCD Table DDL
 
**Assignment Prompt:** 
> Write a DDL statement to create an `actors_history_scd` table that tracks the following fields for each actor in the `actors` table.

**Example solution:**
```sql
```

### Query 4: Actors History SCD Table Batch Backfill Query
This SQL query is designed to populate the 'actors_history_scd' table in the 'student' schema. It is tailored for the task of incrementally backfilling this table with historical data regarding the status and quality classification of actors.
 
**Assignment Prompt:** 
> Write a "backfill" query that can populate the entire `actors_history_scd` table in a single query.

**Example solution:**
```sql

```

### Query 5: Actors History SCD Table Incremental Backfill Query

This SQL script is designed for incrementally updating the 'actors_history_scd' table in the 'student' schema. It aims to integrate the latest year's data (2022) into the historical records.

**Assignment Prompt:** 
> Write an "incremental" query that can populate a single year's worth of the `actors_history_scd` table by combining the previous year's SCD data with the new incoming data from the `actors` table for this year.

**Example solution:**
```sql

```