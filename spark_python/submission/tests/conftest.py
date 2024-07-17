import pytest
from pyspark.sql import SparkSession

# This creates a Spark session with a given application name. It's configured to run locally.
def spark_session_factory(app_name: str) -> SparkSession:
  return (
      SparkSession.builder
      .master("local")
      .appName("chispa")
      .getOrCreate()
  )

# This decorator defines a pytest fixture named spark_session with a session scope, 
# meaning it will be set up once per test session and reused across all tests.
@pytest.fixture(scope='session')
def spark_session():
    return spark_session_factory
