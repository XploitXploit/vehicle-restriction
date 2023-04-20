# CR: sort imports
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import (
    MetaData,
    Column,
    Table,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from sqlalchemy.types import UserDefinedType
from app.settings import settings


class Geometry(UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue)

    def column_expression(self, col):
        return func.ST_AsText(col)


class GeometryBinary(UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"

    def bind_expression(self, bindvalue):
        return func.ST_GeomAsBinary(bindvalue)

    def column_expression(self, col):
        return func.ST_AsBinary(col)


class GeometryJson(UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue)

    def column_expression(self, col):
        return func.ST_AsGeoJSON(col, 3)


def init(
    conn_string: str = settings.PRODUCTION_CONN,
    conn_string_log: str = settings.LOG_CONN,
    autocommit: bool = True,
):
    metadata = MetaData()
    engine = create_engine(conn_string)

    metadata_log = MetaData()
    engine_log = create_engine(conn_string_log)

    # TODO: evaluate ditch reflect and declare tables in sqlalchemy
    metadata.reflect(
        engine,
        only=[
            "aw_vehicle_restriction",
            "aw_vehicle_restriction_condition",
            "aw_vehicle_restriction_action",
            "aw_vehicle",
            "aw_trip",
            "aw_user",
            "aw_notification_template",
            "aw_vehicle_restriction_blacklist",
        ],
    )

    # CR: is it possible to get the awto_log.aw_vehicle_restriction_log from the same
    # engine as above?
    metadata_log.reflect(
        engine_log,
        only=["aw_vehicle_restriction_log", "aw_vehicle_restriction_on_going_log"],
    )

    # this is here to map the table with a custom type (geom)
    # CR: a variable that will be discarded should be named '_'

    _ = Table(
        "aw_vehicle_restriction_polygon",
        metadata,
        Column("polygon_id", Integer, primary_key=True),
        Column("creation_date", DateTime, nullable=False),
        Column("polygon_name", String(255), nullable=False),
        Column("polygon_geom", GeometryJson, nullable=False),
        extend_existing=True,
    )

    Base = automap_base(metadata=metadata)
    Base_log = automap_base(metadata=metadata_log)
    Base.prepare()
    Base_log.prepare()

    (
        VehicleModel,
        RestrictionModel,
        PolygonModel,
        ConditionModel,
        ActionModel,
        TripModel,
        UserModel,
        LogModel,
        OnGoingLogModel,
        NotificationModel,
        BlacklistModel,
    ) = (
        Base.classes.aw_vehicle,
        Base.classes.aw_vehicle_restriction,
        Base.classes.aw_vehicle_restriction_polygon,
        Base.classes.aw_vehicle_restriction_condition,
        Base.classes.aw_vehicle_restriction_action,
        Base.classes.aw_trip,
        Base.classes.aw_user,
        Base_log.classes.aw_vehicle_restriction_log,
        Base_log.classes.aw_vehicle_restriction_on_going_log,
        Base.classes.aw_notification_template,
        Base.classes.aw_vehicle_restriction_blacklist,
    )

    session_maker = sessionmaker(autocommit=autocommit)
    session_maker.configure(bind=engine)
    session_log_maker = sessionmaker(autocommit=autocommit)
    session_log_maker.configure(bind=engine_log)
    session = session_maker()
    session_log = session_log_maker()

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
