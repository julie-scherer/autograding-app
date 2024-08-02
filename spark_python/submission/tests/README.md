
### Local setup

Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies into that virtual environment:
```bash
python -m pip install -r requirements.txt
```

Run tests:
```bash
pytest
```

### Please note

You don't need to explicitly run or import **`conftest.py`**. Pytest handles this for you. Pytest automatically finds and loads **`conftest.py`** in the tests directory. The fixtures defined in **`conftest.py`** become available to all tests. In this case, the spark_session fixture is defined in **`conftest.py`** to create a Spark session that can be used in your tests.

You also do not need to explicitly run or test the **`test_can_import.py`** and **`test_spark_jobs.py`** files. pytest will automatically discover the test files (`test_*.py` or `*_test.py` by default) and execute the test functions inside them. 

When pytest encounters a test function that requires a fixture (like spark_session), it uses the fixture from **`conftest.py`**. For example, if you have a test in **`test_spark_jobs.py`** that uses the spark_session fixture, pytest will call the spark_session function in **`conftest.py`** to create and provide the Spark session for the test.
