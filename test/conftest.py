import pytest
from project.utils import get_env_var_config
from snowflake.snowpark.session import Session

@pytest.fixture(scope='module')
def session(request) -> Session:
    return Session.builder.configs(get_env_var_config()).create()

