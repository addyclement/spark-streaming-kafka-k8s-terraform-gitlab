"""
test if raw transforms extract fufilment type
concat order number correctly
calculates disconted total

2nd tests if look up for ship destination is correct
"""
# https://towardsdatascience.com/the-elephant-in-the-room-how-to-write-pyspark-unit-tests-a5073acabc34
# https://medium.com/swlh/automate-testing-with-gitlab-pipelines-4d35c72c18a

import pytest
# from etl import transform_data
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime
from pyspark.sql import SparkSession

import os

test_path = (os.path.abspath(os.curdir))
print(test_path)

# os.chdir('../code')
print(os.path.abspath(os.curdir))

from bexley_spark_stream_msk_es_04 import transform_json_message

def test_json_transform(spark_fixture):
        #1. Prepare an input data frame that mimics our source data.
        
    input_schema = StructType([ \
            StructField("order_id",IntegerType(),True), \
            StructField("order_total",DoubleType(),True), \
            StructField("ship_to_city_id" ,IntegerType(),True) ,\
            StructField("freight" ,DoubleType(),True), \
            StructField("customer_id" ,IntegerType(),True), \
            StructField("ship_method",StringType(),True),   
            StructField("order_number" ,StringType(),True), \
            StructField("discount_applied" ,DoubleType(),True), \
            StructField("order_date" ,StringType(),True), \
            StructField("order_basket", ArrayType(
                StructType(
                [
                    StructField("order_qty", IntegerType()),
                    StructField("product_id",IntegerType()),
                    StructField("is_discounted",BooleanType())
                    ]
                ))
            )
        ])


    # create an input data frame based on the sample json data provided
    # these contain at least 10 messages that handle the most common type of data expected
    # os.chdir(test_path)

    input_df = spark_fixture.read.json(path= os.path.abspath(os.curdir) +"/sample_messages.json", schema=input_schema, multiLine=True)
    
    #2. Prepare an expected data frame which is the output that we expect.        

    expected_transformed_schema = StructType([
            StructField('order_number', StringType(), True),  
            StructField('discounted_total', DoubleType(), True),
            StructField('data_key', StringType(), True),
            StructField('ship_to_city_id', IntegerType(), True), # StringType
            StructField('order_date', StringType(), True),
            StructField('ship_method', StringType(), True), # 
            StructField('fufilment_type', StringType(), True)
            ])
    # 947.43
    expected_transformed_data = [
                            Row(order_number='5206-5132-5428', discounted_total=947.43, data_key='5206-5132-5428-2022-12-13', ship_to_city_id=1, order_date='2022-12-13T21:19:00.530754', ship_method='Flat rate', fufilment_type='Merchant'), 
                            Row(order_number='6858-3844-7275', discounted_total=336.59, data_key='6858-3844-7275-2022-12-13', ship_to_city_id=45, order_date='2022-12-13T21:28:31.814023', ship_method='Expedited', fufilment_type='Bexley'), 
                            Row(order_number='6718-5444-8144', discounted_total=68.73, data_key='6718-5444-8144-2022-12-14', ship_to_city_id=31, order_date='2022-12-14T16:29:43.932096', ship_method='Same-day delivery', fufilment_type='Merchant'), 
                            Row(order_number='3374-4634-8652', discounted_total=126.28, data_key='3374-4634-8652-2022-12-14', ship_to_city_id=30, order_date='2022-12-14T17:01:50.136703', ship_method='Overnight', fufilment_type='Merchant'), 
                            Row(order_number='9229-5285-5424', discounted_total=138.55, data_key='9229-5285-5424-2022-12-14', ship_to_city_id=63, order_date='2022-12-14T17:01:51.059912', ship_method='2-day shipping', fufilment_type='Merchant'), 
                            Row(order_number='3467-5567-5249', discounted_total=561.7, data_key='3467-5567-5249-2022-12-14', ship_to_city_id=61, order_date='2022-12-14T17:01:52.749579', ship_method='Expedited', fufilment_type='Merchant'), 
                            Row(order_number='3462-3651-6026', discounted_total=118.75, data_key='3462-3651-6026-2022-12-14', ship_to_city_id=51, order_date='2022-12-14T17:01:54.563762', ship_method='Flat rate', fufilment_type='Bexley'), 
                            Row(order_number='3248-3951-8691', discounted_total=217.49, data_key='3248-3951-8691-2022-12-14', ship_to_city_id=21, order_date='2022-12-14T17:01:55.315050', ship_method='Expedited', fufilment_type='Bexley'), 
                            Row(order_number='4583-6214-9446', discounted_total=32.9, data_key='4583-6214-9446-2022-12-14', ship_to_city_id=44, order_date='2022-12-14T17:01:56.343200', ship_method='Freight', fufilment_type='Merchant'), 
                            Row(order_number='2168-5937-6209', discounted_total=949.45, data_key='2168-5937-6209-2022-12-14', ship_to_city_id=26, order_date='2022-12-14T17:01:57.804518', ship_method='2-day shipping', fufilment_type='Merchant'), 
                            Row(order_number='6462-4687-6498', discounted_total=515.1, data_key='6462-4687-6498-2022-12-14', ship_to_city_id=3, order_date='2022-12-14T17:01:59.174798', ship_method='Expedited', fufilment_type='Merchant'), 
                            Row(order_number='3495-3751-7900', discounted_total=283.8, data_key='3495-3751-7900-2022-12-14', ship_to_city_id=33, order_date='2022-12-14T17:02:00.187761', ship_method='Flat rate', fufilment_type='Bexley'), 
                            Row(order_number='1719-6171-8634', discounted_total=939.6, data_key='1719-6171-8634-2022-12-14', ship_to_city_id=59, order_date='2022-12-14T17:02:01.783916', ship_method='Freight', fufilment_type='Merchant')
                            ]
    
    expected_transformed_df =  spark_fixture.createDataFrame(data=expected_transformed_data, schema = expected_transformed_schema)


    #3. Apply our transformation to the input data frame
    

    actual_transformed_df = transform_json_message(json_df=input_df)

    #4. Assert the output of the transformation to the expected data frame.
    """
    field_list = lambda fields: (fields.name, fields.dataType, fields.nullable)
    fields1 = [*map(field_list, actual_transformed_df.schema.fields)]
    fields2 = [*map(field_list, expected_transformed_df.schema.fields)]
    # Compare schema of transformed_df and expected_df
    res = set(fields1) == set(fields2)
    """

    print("expected")
    expected_transformed_df.printSchema()
    expected_transformed_df.show(truncate=False)

    print("actual")
    actual_transformed_df.printSchema()
    actual_transformed_df.show(truncate=False)

    # self.maxDiff = None
    # assert
    # assert fields1 == fields2
    # Compare data in transformed_df and expected_df
    # self.maxDiff = None

    
    assert sorted(expected_transformed_df.collect()) == sorted(actual_transformed_df.collect())


"""
    test_ci:
  script:
    - npm run test
  artifacts:
    paths:
      - coverage/
    reports:
      junit:
        - test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
  coverage: '/All files\s+\|\s+\d+\.\d+/'
"""