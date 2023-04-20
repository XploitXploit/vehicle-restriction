from datetime import datetime
import logging
from sqlalchemy import text
from app.data_acces_layer.log import DAL_Log
from app.data_acces_layer.restriction import DAL_RestrictionModel
from app.data_acces_layer.user import DAL_UserModel
from app.data_acces_layer.vehicle import DAL_VehicleModel

logger = logging.getLogger("vehicle_restriction")


def test_get_conditions_and_restrictions_now(create_models):
    """
    Test get_restrictions
    """
    session = create_models[0]
    restriction_model = create_models[3]
    vehicle_model = create_models[2]
    action_model = create_models[6]
    notification_model = create_models[12]
    blacklist_model = create_models[14]
    dal_restriction = DAL_RestrictionModel(
        session,
        restriction_model,
        vehicle_model,
        action_model,
        notification_model,
        blacklist_model,
    )
    (
        restrictions,
        conditions,
    ) = dal_restriction.get_conditions_and_restrictions_now(datetime.utcnow())
    assert len(restrictions) == 1
    assert len(conditions) == 10


def test_get_user_by_id(create_models):
    """
    Test get_user_by_id
    """
    session = create_models[0]
    user_model = create_models[8]
    dal_user = DAL_UserModel(session, user_model)
    user = dal_user.get_user_by_id(333054)
    assert user.user_id == 333054
    assert user.fname == "Francisco"
    assert user.lname == "Pellerano"
    assert user.email_id == "fpellerano+copihue@awto.cl"


def test_get_user_by_ids(create_models):
    """
    Test get_user_by_id
    """
    session = create_models[0]
    user_model = create_models[8]
    dal_user = DAL_UserModel(session, user_model)
    user = dal_user.get_users_by_ids([333054, 333055])
    assert user[0].user_id == 333054
    assert user[0].fname == "Francisco"
    assert user[0].lname == "Pellerano"
    assert user[0].email_id == "fpellerano+copihue@awto.cl"

    assert user[1].user_id == 333055
    assert user[1].fname == "Francisco_test"
    assert user[1].lname == "Pellerano_test"
    assert user[1].email_id == "fpellerano+copihuetest@awto.cl"


def test_get_vehicles_from_cursor(create_models):
    """
    Test get_vehicles_from_cursor
    """
    session = create_models[0]
    vehicle_model = create_models[2]
    blacklist_model = create_models[14]
    dal_vehicle = DAL_VehicleModel(session, vehicle_model, blacklist_model)
    query = text("SELECT vehicle_id, 2 FROM aw_vehicle ")
    vehicles_in_polygon = session.execute(query)
    tuple_vehicles = []
    for vehicle in vehicles_in_polygon:
        tuple_vehicles.append(vehicle)

    vehicles = dal_vehicle.get_vehicles_from_cursor(tuple_vehicles)
    assert len(vehicles) == 1


def test_filter_query_by_status(create_models):
    """
    Test filter_query_by_status
    """
    session = create_models[0]
    vehicle_model = create_models[2]
    blacklist_model = create_models[14]
    dal_vehicle = DAL_VehicleModel(session, vehicle_model, blacklist_model)
    vehicles = session.query(vehicle_model).all()
    vehicles_filtered = dal_vehicle.filter_query_by_status(vehicles, "ACTIVE")
    assert len(vehicles_filtered) == 1


def test_filter_vehicles_by_plate_pattern_and_status_list(create_models):
    """
    Test filter_vehicles_by_plate_pattern_and_status_list
    """
    session = create_models[0]
    vehicle_model = create_models[2]
    condition_model = create_models[5]
    blacklist_model = create_models[14]
    condition = (
        session.query(condition_model).filter_by(veh_rest_condition_id=9).first()
    )
    dal_vehicle = DAL_VehicleModel(session, vehicle_model, blacklist_model)
    vehicles = dal_vehicle.filter_vehicles_by_plate_pattern_and_status_list(
        condition, ["ACTIVE"]
    )
    assert len(vehicles) == 1


def test_get_logs(create_models):
    """
    Test get_logs
    """
    session_log = create_models[1]
    logs_model = create_models[9]
    dal_logs = DAL_Log(session_log, logs_model)
    logs = dal_logs.get_logs()
    assert len(logs) == 1
    logs = [
        logs_model(
            id=2,
            log_time="2022-06-21 16:52:23",
            restriction_id=2,
            veh_rest_action_id=3,
            polygon_id=2,
            vehicle_id=2554,
        ),
        logs_model(
            id=3,
            log_time="2022-06-21 16:52:23",
            restriction_id=2,
            veh_rest_action_id=3,
            polygon_id=2,
            vehicle_id=2554,
        ),
        logs_model(
            id=4,
            log_time="2022-06-21 16:52:23",
            restriction_id=2,
            veh_rest_action_id=3,
            polygon_id=2,
            vehicle_id=2554,
        ),
        logs_model(
            id=5,
            log_time="2022-06-21 16:52:23",
            restriction_id=2,
            veh_rest_action_id=3,
            polygon_id=2,
            vehicle_id=2554,
        ),
    ]
    session_log.add_all(logs)
    session_log.commit()
    assert len(dal_logs.get_logs()) == 5
    assert len(dal_logs.get_logs(limit=2)) == 2
    for log in logs:
        session_log.delete(log)
    session_log.commit()


def test_get_log_by_id(create_models):
    """
    Test get_log_by_id
    """
    session_log = create_models[1]
    logs_model = create_models[9]
    dal_logs = DAL_Log(session_log, logs_model)
    log = dal_logs.get_log_by_id(12)
    assert log.id == 12


def test_get_logs_by_vehicle_id(create_models):
    """
    Test get_logs_by_vehicle_id
    """
    session_log = create_models[1]
    logs_model = create_models[9]
    dal_logs = DAL_Log(session_log, logs_model)
    logs = dal_logs.get_logs_by_vehicle_id(2554)
    assert len(logs) == 1
    assert logs[0].vehicle_id == 2554


def test_save_log(create_models):
    """
    Test save_log
    """
    session_log = create_models[1]
    logs_model = create_models[9]
    dal_logs = DAL_Log(session_log, logs_model)
    log = logs_model(
        id=1,
        log_time="2022-06-21 16:52:23",
        restriction_id=2,
        veh_rest_action_id=3,
        polygon_id=2,
        vehicle_id=2554,
    )
    dal_logs.save_log(log)
    log = session_log.query(logs_model).filter(logs_model.id == 1).first()
    assert log.id == 1
    session_log.query(logs_model).delete()
    session_log.commit()


def test_save_bulk_logs(create_models):
    """
    Test save_bulk_logs
    """
    session_log = create_models[1]
    logs_model = create_models[9]
    dal_logs = DAL_Log(session_log, logs_model)
    logs = [
        logs_model(
            id=2,
            log_time="2022-06-21 16:52:23",
            restriction_id=2,
            veh_rest_action_id=3,
            polygon_id=2,
            vehicle_id=2554,
        ),
        logs_model(
            id=3,
            log_time="2022-06-21 16:52:23",
            restriction_id=2,
            veh_rest_action_id=3,
            polygon_id=2,
            vehicle_id=2554,
        ),
    ]
    dal_logs.save_bulk_logs(logs)
    logs = session_log.query(logs_model).all()
    assert len(logs) == 2
    assert logs[0].id == 2
    assert logs[1].id == 3
    session_log.query(logs_model).delete()
    session_log.commit()


def test_check_vehicles_in_restrictions_polygons(create_models):
    """
    Test check_vehicles_in_restrictions_polygons
    """
    session = create_models[0]
    vehicle_model = create_models[2]
    condition_model = create_models[5]
    restriction_model = create_models[3]
    action_model = create_models[6]
    notification_model = create_models[12]
    blacklist_model = create_models[14]

    vehicles = [session.query(vehicle_model).filter_by(vehicle_id=2668).first()]
    condition = (
        session.query(condition_model).filter_by(veh_rest_condition_id=9).first()
    )
    vehicle_list = []

    dal_restriction_model = DAL_RestrictionModel(
        session,
        restriction_model,
        vehicle_model,
        action_model,
        notification_model,
        blacklist_model,
    )
    dal_restriction_model.check_vehicles_in_restrictions_polygons(
        vehicles, condition, vehicle_list
    )

    assert len(vehicle_list[0][0]) == 1
    assert vehicle_list[0][0][0].vehicle_id == 2668


def test_check_vehicles_out_restrictions_polygons(create_models):
    """
    Test check_vehicles_in_restrictions_polygons
    """
    session = create_models[0]
    vehicle_model = create_models[2]
    condition_model = create_models[5]
    restriction_model = create_models[3]
    action_model = create_models[6]
    notification_model = create_models[12]
    blacklist_model = create_models[14]

    vehicles = [session.query(vehicle_model).filter_by(vehicle_id=2668).first()]
    condition = (
        session.query(condition_model).filter_by(veh_rest_condition_id=9).first()
    )
    condition.polygon_id = 1
    vehicles_set = set()

    dal_restriction_model = DAL_RestrictionModel(
        session,
        restriction_model,
        vehicle_model,
        action_model,
        notification_model,
        blacklist_model,
    )
    dal_restriction_model.check_vehicles_out_restrictions_polygons(
        vehicles, condition, vehicles_set
    )
    assert len(vehicles_set) == 1
    assert list(vehicles_set)[0].vehicle_id == 2668


def test_exclude_blacklist_models(create_models):
    session = create_models[0]
    vehicle_model = create_models[2]
    blacklist_model = create_models[14]

    dal_vehicle_model = DAL_VehicleModel(session, vehicle_model, blacklist_model)
    vehicle = {
        "vehicle_id": 9,
        "vehicle_name": None,
        "vehicle_number_plate": None,
        "vehicle_model": "CUX",
        "vehicle_type": "Scooter",
        "type_of_operation": "FREE_FLOAT",
        "vehicle_image_url": "http://storage.bhs.cloud.ovh.net/v1/AUTH_e8b3935ef608462ebc9cefa06e286b5e/public_gowgo_storage_brasil/vehicle-model/voltz_ev1plus.png",
        "current_zone": "15",
        "vehicle_price": None,
        "vehicle_status": None,
        "vehicle_current_status": "DEACTIVE",
        "inventory_status": None,
        "vehicle_make": "Supersoco",
        "box_num": None,
        "provider_device_id": 7,
        "external_device_id": "V4X203XHE61004",
        "box_model": None,
        "sim_provider": None,
        "transmission": "AUTOMATIC",
        "combustible": "ELECTRIC",
        "fuel_percent": 0.0000,
        "patent": "MSS01",
        "device_id": "2787313",
        "external_provider": None,
        "observation": None,
        "kilometer": 0,
        "fleet_vehicle_id": None,
        "latitude": None,
        "longitude": None,
        "current_user_id": None,
        "creation_date": "2022-02-21 18:03:28",
        "last_modified_date": "2022-10-14 13:35:37",
        "vehicle_segment_id": None,
        "priority": "D",
        "voltage": None,
        "cv": None,
        "cvl": None,
        "ignition_on": 0,
        "model_year": None,
        "num_chasis": "",
        "purchase_date": None,
        "install_date": None,
        "device_model": None,
        "device_version": None,
        "sim_card": None,
        "temporal_parking": 0,
        "disconnection_device_check": 0,
        "cron_voltage": 0.0000,
        "key_status": None,
        "last_sync_position": "2022-03-08 15:30:14",
    }
    to_exclude_vehicle = vehicle_model(**vehicle)
    session.add(to_exclude_vehicle)
    session.commit()
    vehicle_list = session.query(vehicle_model).all()

    blacklisted = dal_vehicle_model.exclude_blacklist_models(vehicle_list)
    print(blacklisted)
    assert len(blacklisted) == 1
    session.query(vehicle_model).filter(vehicle_model.vehicle_id == 9).delete()
    session.commit()
