import pytest
from jobs.job_1 import job_1

# FAKE EXAMPLE
def test_job_1(spark_session):
    output_table_name = "test_table"
    
    # Create a test DataFrame
    data = [("Alice", 1), ("Bob", 2)]
    columns = ["name", "value"]
    
    # Use spark_session fixture to create a Spark session
    test_df = spark_session.createDataFrame(data, columns)
    
    # Register the DataFrame as a temp table
    test_df.createOrReplaceTempView(output_table_name)
    
    # Call the job_1 function
    result_df = job_1(spark_session, output_table_name)
    
    # Perform assertions on the result_df
    assert result_df is not None
    assert result_df.count() == 2
