from typing import List
from app.utilities import utl_restriction


class DAL_VehicleModel:
    def __init__(self, session, vehicle_model, blacklist_model):
        self.session = session
        self.VehicleModel = vehicle_model
        self.BlackListModel = blacklist_model

    def get_vehicles_from_cursor(self, vehicles_cursor: List[tuple]):
        vehicles_response_id = [id for id, polygon in vehicles_cursor]
        return (
            self.session.query(self.VehicleModel)
            .filter(self.VehicleModel.vehicle_id.in_(vehicles_response_id))
            .all()
        )

    def get_vehicle_by_user_id(self, user_id):
        return (
            self.session.query(self.VehicleModel)
            .filter(self.VehicleModel.current_user_id == user_id)
            .first()
        )

    def filter_query_by_status(self, vehicles_list, status):
        filtered = filter(lambda x: x.vehicle_current_status == status, vehicles_list)
        return list(filtered)

    def filter_vehicles_by_status(self, status):
        return (
            self.session.query(self.VehicleModel)
            .filter(self.VehicleModel.vehicle_current_status == status)
            .all()
        )

    def filter_vehicles_by_plate_pattern_and_status_list(self, condition, status_list):
        return (
            self.session.query(self.VehicleModel)
            .filter(
                self.VehicleModel.patent.op("regexp")(
                    utl_restriction.create_regex_pattern(condition.plate_pattern)
                ),
                self.VehicleModel.vehicle_current_status.in_(status_list),
            )
            .all()
        )

    def exclude_blacklist_models(self, vehicles_list):
        blacklist = [
            v.vehicle_model for v in self.session.query(self.BlackListModel).all()
        ]
        return [
            vehicle
            for vehicle in vehicles_list
            if vehicle.vehicle_model not in blacklist
        ]
