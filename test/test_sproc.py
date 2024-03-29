from project.sproc import create_fact_tables
from snowflake.snowpark.types import *


def test_create_fact_tables(request, session):
    if request.config.getoption('--snowflake-session', default=None) == 'local':
        from patches import patch_monthname
    DB = 'CITIBIKE'
    SCHEMA = 'TEST'
    TABLE = 'TRIPS_TEST'

    # Set up source table
    tbl = session.create_dataframe(
        data=[
            [1983, '2018-03-01 09:47:00.000 +0000', 551, 30958],
            [1988, '2018-03-01 09:47:01.000 +0000', 242, 19278],
            [1992, '2018-03-01 09:47:01.000 +0000', 768, 18461],
            [1980, '2018-03-01 09:47:03.000 +0000', 690, 15533],
            [1991, '2018-03-01 09:47:03.000 +0000', 490, 32449],
            [1959, '2018-03-01 09:47:04.000 +0000', 457, 29411],
            [1971, '2018-03-01 09:47:08.000 +0000', 279, 28015],
            [1964, '2018-03-01 09:47:09.000 +0000', 546, 15148],
            [1983, '2018-03-01 09:47:11.000 +0000', 358, 16967],
            [1985, '2018-03-01 09:47:12.000 +0000', 848, 20644],
            [1984, '2018-03-01 09:47:14.000 +0000', 295, 16365]
        ],
        schema=['BIRTH_YEAR', 'STARTTIME', 'TRIPDURATION',	'BIKEID'],
    )

    tbl.write.mode('overwrite').save_as_table([DB, SCHEMA, TABLE], mode='overwrite')

    # Expected values
    n_rows_expected = 12 
    bike_facts_expected = session.create_dataframe(
        data=[
            [30958, 1, 551.0, 41.0], 
            [19278, 1, 242.0, 36.0], 
            [18461, 1, 768.0, 32.0],
            [15533, 1, 690.0, 44.0], 
            [32449, 1, 490.0, 33.0], 
            [29411, 1, 457.0, 65.0], 
            [28015, 1, 279.0, 53.0], 
            [15148, 1, 546.0, 60.0], 
            [16967, 1, 358.0, 41.0], 
            [20644, 1, 848.0, 39.0], 
            [16365, 1, 295.0, 40.0]
        ],
        schema=StructType([
            StructField("BIKEID", IntegerType()), 
            StructField("COUNT", IntegerType()), 
            StructField("AVG_TRIPDURATION", FloatType()), 
            StructField("AVG_RIDER_AGE", FloatType())
        ])
    ).collect()

    month_facts_expected = session.create_dataframe(
        data=[['Mar', 11, 502.18182, 43.00000]],
        schema=StructType([
            StructField("MONTH", StringType()), 
            StructField("COUNT", IntegerType()), 
            StructField("AVG_TRIPDURATION", DecimalType()), 
            StructField("AVG_RIDER_AGE", DecimalType())
        ])
    ).collect()

    # Call sproc, get actual values
    n_rows_actual = create_fact_tables(session, SCHEMA, TABLE)
    bike_facts_actual = session.table([DB, SCHEMA, 'bike_facts']).collect() 
    month_facts_actual = session.table([DB, SCHEMA, 'month_facts']).collect() 

    # Comparisons
    assert n_rows_expected == n_rows_actual
    assert bike_facts_expected == bike_facts_actual
    #assert month_facts_expected ==  month_facts_actual