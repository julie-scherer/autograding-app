## Week 1 Queries and Solutions

### Query 1: Actors Table DDL

**Assignment Prompt:** 
> Write a DDL query to create an `actors` table.

**Example solution:**
```sql
CREATE OR REPLACE TABLE actors (
actor VARCHAR,
actor_id VARCHAR,
films ARRAY(
  ROW(
    year INTEGER,
    film VARCHAR,
    votes INTEGER,
    rating DOUBLE,
    film_id VARCHAR
  )
),
quality_class VARCHAR,
is_active BOOLEAN,
current_year INTEGER
) WITH (
FORMAT = 'PARQUET', partitioning = ARRAY ['current_year']
)
```
### Query 2: Cumulative Table Computation Query
This query populates the actors table by combining data from two different years.

**Assignment Prompt:** 
> Write a query that populates the `actors` table one year at a time.

**Example solution:**
```sql
INSERT INTO actors 
WITH yesterday AS (
    SELECT * FROM actors
    WHERE current_year = 1914
    ),
today AS (
    SELECT * FROM bootcamp.actor_films
    WHERE year = 1915
) 
SELECT
    COALESCE(y.actor, t.actor) AS actor,
    COALESCE(y.actor_id, t.actor_id) AS actor_id,
    CASE
        WHEN y.films IS NULL THEN ARRAY_AGG( (ROW(t.year,t.film,t.votes,t.rating,t.film_id)) )
        WHEN t.year IS NOT NULL THEN y.films || ARRAY_AGG( (ROW(t.year,t.film,t.votes,t.rating,t.film_id)) )
        ELSE y.films
    END,
    CASE
        WHEN AVG(t.rating) IS NOT NULL
            THEN (
            CASE
            WHEN AVG(t.rating) > 8 THEN 'star'
            WHEN AVG(t.rating) > 7 THEN 'good'
            WHEN AVG(t.rating) > 6 THEN 'average'
            ELSE 'bad'
            END
        )
        ELSE y.quality_class
    END,
    CASE
        WHEN t.actor_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS is_active,
    COALESCE(t.year, y.current_year + 1) AS current_year
FROM yesterday y 
FULL OUTER JOIN today t ON y.actor_id = t.actor_id
GROUP BY y.actor, t.actor, y.actor_id, t.actor_id, y.films, t.year, y.current_year, y.quality_class
```
### Query 3: Actors History SCD Table DDL
 
**Assignment Prompt:** 
> Write a DDL statement to create an `actors_history_scd` table that tracks the following fields for each actor in the `actors` table.

**Example solution:**
```sql
CREATE OR REPLACE TABLE actors_history_scd (
  actor VARCHAR,
  quality_class VARCHAR,
  is_active BOOLEAN,
  start_date INTEGER,
  end_date INTEGER,
  current_year INTEGER 
) WITH (
  FORMAT = 'PARQUET',
  partitioning = ARRAY ['current_year'] 
)
```

### Query 4: Actors History SCD Table Batch Backfill Query
This SQL query is designed to populate the 'actors_history_scd' table in the 'student' schema. 
It is tailored for the task of incrementally backfilling this table with historical data 
regarding the status and quality classification of actors.
 
**Assignment Prompt:** 
> Write a "backfill" query that can populate the entire `actors_history_scd` table in a single query.

**Example solution:**
```sql
INSERT INTO actors_history_scd
WITH lagged AS (
  SELECT
    actor,
    actor_id,
    quality_class,
    is_active,
    LAG(quality_class, 1) OVER ( PARTITION BY actor_id ORDER BY current_year ) AS previous_quality_class,
    LAG(is_active, 1) OVER ( PARTITION BY actor_id ORDER BY current_year ) AS previous_is_active,
    current_year
  FROM actors
  WHERE current_year <= 2021 
),
streaked AS (
  SELECT *,
    SUM(
      CASE
        WHEN quality_class <> previous_quality_class THEN 1
        WHEN is_active <> previous_is_active THEN 1
        ELSE 0
      END
    ) OVER ( PARTITION BY actor_id ORDER BY current_year ) AS streak_identifier
  FROM lagged
) 
SELECT
  actor,
  quality_class,
  is_active,
  MIN(current_year) AS start_date,
  MAX(current_year) AS end_date,
  2021 AS current_year
FROM streaked 
GROUP BY actor, quality_class, is_active, streak_identifier
```

### Query 5: Actors History SCD Table Incremental Backfill Query

This SQL script is designed for incrementally updating the 'actors_history_scd' table in the 'student' schema. 
It aims to integrate the latest year's data (2022) into the historical records.

**Assignment Prompt:** 
> Write an "incremental" query that can populate a single year's worth of the `actors_history_scd` table by combining the previous year's SCD data with the new incoming data from the `actors` table for this year.

**Example solution:**
```sql
INSERT INTO actors_history_scd 
WITH last_year_scd AS (
  SELECT *
  FROM actors_history_scd
  WHERE current_year = 2021
),
current_year_scd AS (
  SELECT *
  FROM actors
  WHERE current_year = 2022
),
combined AS (
  SELECT
    COALESCE(ly.actor, cy.actor) AS actor,
    COALESCE(ly.start_date, cy.current_year) AS start_date,
    COALESCE(ly.end_date, cy.current_year) AS end_date,
    CASE
      WHEN ( ly.quality_class <> cy.quality_class OR ly.is_active <> cy.is_active ) THEN 1
      WHEN ( ly.quality_class = cy.quality_class AND ly.is_active = cy.is_active ) THEN 0
    END AS did_change,
    ly.quality_class AS quality_class_last_year,
    cy.quality_class AS quality_class_this_year,
    ly.is_active AS is_active_last_year,
    cy.is_active AS is_active_this_year,
    2022 AS current_year
  FROM last_year_scd ly 
  FULL OUTER JOIN current_year_scd cy
    ON ly.actor = cy.actor
    AND ly.end_date + 1 = cy.current_year
),
changes AS (
  SELECT
    actor,
    current_year,
    CASE
      WHEN did_change = 0
        THEN ARRAY [
          CAST( ROW (quality_class_last_year,is_active_last_year,start_date,end_date + 1) AS ROW (quality_class VARCHAR,is_active BOOLEAN,start_date INTEGER,end_date INTEGER) )
        ]
      WHEN did_change = 1
        THEN ARRAY [
          CAST( ROW (quality_class_last_year,is_active_last_year,start_date,end_date) AS ROW (quality_class VARCHAR,is_active BOOLEAN,start_date INTEGER,end_date INTEGER ) ),
          CAST( ROW (quality_class_this_year,is_active_this_year,current_year,current_year) AS ROW (quality_class VARCHAR,is_active BOOLEAN,start_date INTEGER,end_date INTEGER) )
        ]
      WHEN did_change IS NULL
        THEN ARRAY [
          CAST( ROW (COALESCE(quality_class_last_year, quality_class_this_year),COALESCE(is_active_last_year, is_active_this_year),start_date,end_date) AS ROW (quality_class VARCHAR,is_active BOOLEAN,start_date INTEGER,end_date INTEGER) )
        ]
    END AS change_array
  FROM combined
) 
SELECT
  actor,
  arr.quality_class,
  arr.is_active,
  arr.start_date,
  arr.end_date,
  current_year
FROM changes
CROSS JOIN UNNEST(change_array) AS arr
```
