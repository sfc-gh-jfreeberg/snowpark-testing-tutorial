from snowflake.snowpark.session import Session

session = Session.builder.config('local_testing', True).create()

df = session.create_dataframe([[1,2],[3,4]], ['a', 'b'])

df.with_column('c', df['a']+df['b']).show()