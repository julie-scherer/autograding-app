## Example Solution:

To aid in your review, an example solution is provided below:

Key details of this solution include:
- **Query Conversion**: Backfill query for `actors_history_scd` have been converted from TrinoSQL to SparkSQL.
- **PySpark Jobs**: New PySpark job has been added under the `src/jobs` directory.
- **Tests**: Corresponding tests have been created in the `src/unit_tests` folder, which employ fake input and expected output data to ensure functionality.

### Example job: `src/jobs/actors_scd_job.py`
- Implemented Slowly Changing Dimensions (SCD) handling for actors' data.
- Identifies changes in actors' `quality_class` and `is_active` status, and then groups and orders them for final output.

```python
# Import required libraries and modules
from pyspark.sql import SparkSession

def actors_scd_job(spark: SparkSession, output_table_name: str):
    """Performs the SCD transformation on actors data.

    Args:
        spark (SparkSession): Spark session object.
        dataframe (DataFrame): Input dataframe containing actor data.

    Returns:
        DataFrame: Transformed dataframe with SCD details.
    """
    # Define the SQL transformation query to compute actor's streaks.
    query = """
        WITH with_previous AS (
            SELECT 
                actor,
                current_year,
                quality_class,
                is_active,
                LAG(quality_class, 1) OVER (PARTITION BY actorid ORDER BY current_year) AS previous_quality_class,
                LAG(is_active, 1) OVER (PARTITION BY actorid ORDER BY current_year) AS previous_is_active
            FROM actors
            WHERE current_year <= 2021),
            with_indicators AS (
            SELECT *,
                CASE 
                WHEN quality_class <> previous_quality_class THEN 1
                WHEN is_active <> previous_is_active THEN 1
                ELSE 0
                END AS change_indicator
            FROM with_previous),
        with_streaks AS (
            SELECT *,
                SUM(change_indicator) OVER(PARTITION BY actor ORDER BY current_year) AS streak_identifier
                FROM with_indicators
        )
        SELECT 
            actor,
            quality_class,
            is_active,
            MIN(current_year) AS start_date,
            MAX(current_year) AS end_date
        FROM with_streaks
        GROUP BY actor, quality_class, is_active, streak_identifier
        ORDER BY actor, streak_identifier
    """

    output_df = spark.table(output_table_name)

    # Register the input dataframe as a temporary table for SQL processing
    output_df.createOrReplaceTempView(output_table_name)

    # Execute the transformation query and return the resultant dataframe
    return spark.sql(query)

def main():
    """Main function to initiate the SCD transformation."""
    output_table_name = "actors_scd"

    # Create a spark session
    spark = SparkSession.builder \
      .master("local") \
      .appName("actors_scd_job") \
      .getOrCreate()

    # Execute the SCD transformation
    output_df = actors_scd_job(spark, output_table_name)

    # Write the resultant dataframe to the output table
    output_df.write.mode("overwrite").insertInto(output_table_name)
```

### Example tests: `src/unit_tests/test_actors_scd.py`
- Tests the SCD transformation process by checking the transformed actors' data against the expected results.

```python
from chispa.dataframe_comparer import *
from ..jobs.actors_scd_job import actors_scd_job
from collections import namedtuple

# Define the named tuple for the actor's data structure
Actors = namedtuple("Actors", "actorid actor quality_class is_active current_year")
ActorScd = namedtuple("ActorScd", "actor quality_class is_active start_date end_date")

def run_test(spark, source_data, expected_data):
    """
    A helper function to streamline the testing process for SCD transformations.

    Args:
    - spark (SparkSession): The active Spark session.
    - source_data (list): The input list of namedtuples representing actor data.
    - expected_data (list): The list of namedtuples representing the expected transformation results.
    - transformation_func (function): The SCD transformation function to be tested.

    Returns:
    None. It asserts the equality of the transformation result with the expected result.
    """

    # Convert the source data into a DataFrame
    source_df = spark.createDataFrame(source_data)

    # Apply the given SCD transformation on the source data
    actual_df = actors_scd_job(spark, source_df)

    # Convert the expected data into a DataFrame
    expected_df = spark.createDataFrame(expected_data)

    # Assert that the actual transformation result matches the expected result
    assert_df_equality(actual_df, expected_df)

# Positive Test Cases:
def test_is_active_scd_generation(spark: SparkSession):
    """
    This test checks if changing the 'is_active' attribute correctly resets the SCD streak.
    Args:
    - spark (SparkSession): The active Spark session.
    """
    # Define sample data to test this functionality
    source_data = [
        Actors("nm0000472", "Boris Karloff", "average", True, 1920),
        Actors("nm0000472", "Boris Karloff", "average", False, 1921),
        Actors("nm0000472", "Boris Karloff", "average", True, 1922)
    ]

    # Expected output for the transformation
    expected_data = [
        ActorScd("Boris Karloff", 'average', True, 1920, 1920),
        ActorScd("Boris Karloff", 'average', False, 1921, 1921),
        ActorScd("Boris Karloff", 'average', True, 1922, 1922)
    ]

    # Use the run_test helper to validate the transformation
    run_test(spark, source_data, expected_data)

def test_quality_class_scd_generation(spark):
    """
    Ensure changing the quality_class resets the SCD streak.

    Args:
    - spark: The Spark session.
    """
    # Define sample data to test this functionality
    source_data = [
        Actors("nm0000036", "Buster Keaton", "bad", True, 1920),
        Actors("nm0000036", "Buster Keaton", "good", True, 1921),
        Actors("nm0000036", "Buster Keaton", "bad", True, 1922)
    ]

    # Expected output for the transformation
    expected_data = [
        ActorScd("Buster Keaton", 'bad', True, 1920, 1920),
        ActorScd("Buster Keaton", 'good', True, 1921, 1921),
        ActorScd("Buster Keaton", 'bad', True, 1922, 1922)
    ]

    # Use the run_test helper to validate the transformation
    run_test(spark, source_data, expected_data)

def test_data_with_no_changes(spark: SparkSession):
    """
        Ensure no changes in quality_class or is_active across years.

        Args:
        - spark: The Spark session.
        """
    # Define sample data to test this functionality
    source_data = [
        Actors("nm000010", "Alice", "good", True, 1920),
        Actors("nm000010", "Alice", "good", True, 1921),
        Actors("nm000010", "Alice", "good", True, 1922)
    ]

    # Expected output for the transformation
    expected_data = [
        ActorScd("Alice", 'good', True, 1920, 1922)
    ]

    # Use the run_test helper to validate the transformation
    run_test(spark, source_data, expected_data)

# Edge Test cases:
def test_boundary_year_scd_generation(spark: SparkSession):
    """
    This test verifies the SCD transformation's behavior with boundary years.
    Args:
    - spark (SparkSession): The active Spark session.
    """
    # Test data for boundary years (minimum and maximum years)
    source_data = [
        Actors("nm0000090", "John Doe", "good", True, 1920),  # Minimum year
        Actors("nm0000090", "John Doe", "good", True, 2021)  # Maximum year
    ]

    # Expected output for the transformation
    expected_data = [
        ActorScd("John Doe", "good", True, 1920, 2021)
    ]

    # Use the run_test helper to validate the transformation
    run_test(spark, source_data, expected_data)
```
