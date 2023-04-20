from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Json
from decimal import Decimal


# TODO: Create similar models from database models!!! sniff sniff
# TODO: Optional Values???
class Restriction(BaseModel):
    restriction_id: int
    restriction_name: str
    creation_date: datetime
    last_modified_date: datetime
    is_active: bool
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True


class RestrictionCondition(BaseModel):
    veh_rest_condition_id: int  # TODO: not null
    restriction_id: int  # not null
    zone_id: int  # optional
    polygon_id: Optional[int]  # TODO: Optional
    interval_definition: str  # not null
    plate_pattern: str  # not null

    class Config:
        orm_mode = True


class Interval(BaseModel):
    start_time: datetime
    end_time: datetime


class RestrictionAction(BaseModel):
    veh_rest_action_id: int
    restriction_id: int
    is_on_enter: bool
    pre_restriction_status_name: str
    restriction_status_name: str
    notification_id: int

    class Config:
        orm_mode = True


class Vehicle(BaseModel):
    vehicle_id: int
    type: Optional[str]
    vehicle_number_plate: Optional[str]
    vehicle_model: str
    vehicle_status: Optional[int]
    latitude: Decimal
    longitude: Decimal
    vehicle_current_status: Optional[str]
    last_sync_position: datetime

    class Config:
        orm_mode = True


class RestrictionPolygon(BaseModel):
    polygon_id: int
    creation_date: datetime
    polygon_name: str
    polygon_geom: Json

    class Config:
        orm_mode = True


class RestrictionLog(BaseModel):
    id: int
    log_time: datetime
    restriction_id: int
    veh_rest_action_id: int
    polygon_id: int
    vehicle_id: int

    class Config:
        orm_mode = True
