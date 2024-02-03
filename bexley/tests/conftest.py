import pytest
from pyspark.sql import SparkSession
# from pyspark.testing.utils import assertDataFrameEqual
# https://betterprogramming.pub/understand-5-scopes-of-pytest-fixtures-1b607b5c19ed

# scope="session"
@pytest.fixture(scope="session")
def spark_fixture():
    spark = SparkSession.builder.appName("Bexley Test Pipeline").getOrCreate()
    yield spark