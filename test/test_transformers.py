from project.transformers import add_rider_age, calc_bike_facts, calc_month_facts
from snowflake.snowpark.types import StructType, StructField, IntegerType, FloatType


def test_add_rider_age(session):
    input = session.create_dataframe(
        [
            [1980], 
            [1995], 
            [2000]
        ], 
        schema=StructType([StructField("BIRTH_YEAR", IntegerType())])
    )

    expected = session.create_dataframe(
        [
            [1980, 44], 
            [1995, 29], 
            [2000, 24]
        ],
        schema=StructType([StructField("BIRTH_YEAR", IntegerType()), StructField("RIDER_AGE", IntegerType())])
    )
    
    actual = add_rider_age(input)
    assert expected.collect() == actual.collect()


def test_calc_bike_facts(session):
    input = session.create_dataframe([
            [1, 10, 20],
            [1, 5, 30],
            [2, 20, 50],
            [2, 10, 60]
        ], 
        schema=StructType([
            StructField("BIKEID", IntegerType()), 
            StructField("TRIPDURATION", IntegerType()), 
            StructField("RIDER_AGE", IntegerType())
        ])
    )

    expected = session.create_dataframe([
            [1, 2, 7.5, 25.0],
            [2, 2, 15.0, 55.0],
        ], 
        schema=StructType([
            StructField("BIKEID", IntegerType()), 
            StructField("COUNT", IntegerType()), 
            StructField("AVG_TRIPDURATION", FloatType()), 
            StructField("AVG_RIDER_AGE", FloatType())
        ])
    )

    actual = calc_bike_facts(input)
    assert expected.collect() == actual.collect()


def test_calc_month_facts(request, session):
    if request.config.getoption('--snowflake-session', default=None) == 'local':
        from patches import patch_monthname

    input = session.create_dataframe(
        data=[
            ['2018-03-01 09:47:00.000 +0000', 1, 10,  15],
            ['2018-03-01 09:47:14.000 +0000', 2, 20, 12],
            ['2018-04-01 09:47:04.000 +0000', 3, 6,  30]
        ],
        schema=['STARTTIME', 'BIKE_ID', 'TRIPDURATION', 'RIDER_AGE']
    )

    expected = session.create_dataframe(
        data=[
            ['Mar', 2, 15, 13.5],
            ['Apr', 1, 6, 30.0]
        ],
        schema=['MONTH', 'COUNT', 'AVG_TRIPDURATION', 'AVG_RIDER_AGE']
    )

    actual = calc_month_facts(input)

    assert expected.collect() == actual.collect()