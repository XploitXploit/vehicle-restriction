import os
import pytest
from sqlalchemy import create_engine
from app.data_acces_layer.models import init


@pytest.fixture
def create_test_engine():
    engine = create_engine(os.environ.get("MYSQL_TEST_CONN"))
    return engine


@pytest.fixture(scope="function")
def create_models():
    (
        session,
        session_log,
        VehicleModel,
        RestrictionModel,
        PolygonModel,
        ConditionModel,
        ActionModel,
        TripModel,
        UserModel,
        LogModel,
        engine,
        engine_log,
        NotificationModel,
        OnGoingLogModel,
        BlacklistModel,
    ) = init(
        conn_string=os.environ.get("MYSQL_TEST_CONN"),
        conn_string_log=os.environ.get("MYSQL_TEST_CONN_LOG"),
        autocommit=False,
    )
    return (
        session,
        session_log,
        VehicleModel,
        RestrictionModel,
        PolygonModel,
        ConditionModel,
        ActionModel,
        TripModel,
        UserModel,
        LogModel,
        engine,
        engine_log,
        NotificationModel,
        OnGoingLogModel,
        BlacklistModel,
    )
