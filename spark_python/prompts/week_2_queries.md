## Week 2 Queries and Solutions

### Query 1: De-dupe Query

**Assignment Prompt:** 
> Write a query to de-duplicate the `nba_game_details` table from the day 1 lab of the fact modeling week 2 so there are no duplicate values.

**Example solution:**
```sql
WITH deduped AS (
    SELECT *,
      ROW_NUMBER() OVER (
        PARTITION BY
          game_id,
          team_id,
          player_id
      ) AS row_num
    FROM bootcamp.nba_game_details
  )
SELECT * FROM deduped
WHERE row_num = 1
```

### Query 2: User Devices Activity Datelist DDL

**Assignment Prompt:** 
> Write a DDL statement to create a cumulating user activity table by device.

**Example solution:**
```sql
create table user_devices_cumulated (
  user_id bigint,
  browser_type varchar,
  dates_active array(date),
  date date
) with (
  format = 'parquet', partitioning = array['date']
)
```

### Query 3: User Devices Activity Datelist Implementation

**Assignment Prompt:** 
> Write the incremental query to populate the table you wrote the DDL for in the above question from the `web_events` and `devices` tables.

**Example solution:**
```sql
with yesterday as (
  select * from user_devices_cumulated
  where date = date('2022-12-31')
), today as (
  select
    user_id,
    d.browser_type,
    cast(date_trunc('day', event_time) as date) as event_date,
    count(1) 
  from bootcamp.web_events as we left join bootcamp.devices as d on we.device_id = d.device_id
  where date_trunc('day', event_time) = date('2023-01-01')
  group by 1, 2, 3
)
select
  coalesce(yesterdays.user_id, todays.user_id) as user_id,
  coalesce(yesterdays.browser_type, todays.browser_type) as browser_type,
  case
    when yesterdays.dates_active is not null then array[todays.event_date] || yesterdays.dates_active
    else array[todays.event_date]
  end as dates_active,
  date('2023-01-01') as date
from yesterday as yesterdays full outer join today as todays
  on yesterdays.user_id = todays.user_id
```

### Query 4: Cumulative User Devices Int Datelist Implementation

**Assignment Prompt:** 
> Building on top of the previous question, convert the date list implementation into the base-2 integer datelist.

**Example solution:**
```sql
with today as (
  select *
  from user_devices_cumulated
  where date = date('2023-01-07')
)
select
  user_id,
  browser_type,
  to_base(cast(sum(case
    when contains(dates_active, sequence_date) 
      then pow(2, 31 - date_diff('day', sequence_date, date))
    else 0
  end) as bigint), 2) as base_2_datelist
from today cross join unnest(sequence(date('2023-01-01'), date('2023-01-07'))) as t(sequence_date)
group by 1, 2
```

### Query 5: Host Daily Web Metrics DDL

**Assignment Prompt:** 
> Write a DDL statement to create a `hosts_cumulated` table.

**Example solution:**
```sql
create table hw_daily_host_web_metrics (
  host varchar,
  metric_name varchar,
  metric_value bigint,
  date date
) with (
  format = 'parquet', partitioning = array['metric_name', 'date']
)
```

### Query 6: Host Daily Web Metrics Implementation

**Assignment Prompt:** 
> Write a query to incrementally populate the `hosts_cumulated` table from the `web_events` table.

**Example solution:**
```sql
insert into hw_daily_host_web_metrics
select
  host,
  'visits' as metric_name,
  count(1) as metric_value,
  cast(event_time as date) as date
from bootcamp.web_events
group by host, cast(event_time as date)
```

### Query 7: Reduced Host Fact Array DDL

**Assignment Prompt:** 
> Write a DDL statement to create a monthly `host_activity_reduced` table.

**Example solution:**
```sql
create table hw_monthly_array_host_web_metrics (
  host varchar,
  metric_name varchar,
  metric_array array(integer),
  month_start varchar
) with (
  format = 'parquet', partitioning = array['metric_name', 'month_start']
)
```

### Query 8: Reduced Host Fact Array Implementation

**Assignment Prompt:** 
> Write a query to incrementally populate the `host_activity_reduced` table from a `daily_web_metrics` table.

**Example solution:**
```sql
insert into hw_monthly_array_host_web_metrics
with yesterday as (
  select * from hw_monthly_array_host_web_metrics
  where month_start = '2023-08-01'
), today as (
  select * from hw_daily_host_web_metrics
  where date = date('2023-08-02')
)
select
  coalesce(todays.host, yesterdays.host) as host,
  coalesce(todays.metric_name, yesterdays.metric_name) as metric_name,
  coalesce(
    yesterdays.metric_array, 
    repeat(null, cast(date_diff('day', date('2023-08-01'), todays.date) as integer))
  ) || array[todays.metric_value] as metric_array,
  '2023-08-01' as month_start
from today as todays full outer join yesterday as yesterdays
  on todays.host = yesterdays.host and 
    todays.metric_name = yesterdays.metric_name
```