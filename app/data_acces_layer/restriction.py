import logging
from app.data_acces_layer.vehicle import DAL_VehicleModel
from app.settings import settings
from sqlalchemy import text
from sqlalchemy.sql import bindparam


class DAL_RestrictionModel:
    """
    Data Access Layer for the Restriction Model
    """

    def __init__(
        self,
        session,
        restriction_model,
        vehicle_model,
        action_model,
        notification_model,
        blacklist_model,
    ):
        self.session = session
        self.RestrictionModel = restriction_model
        self.ActionModel = action_model
        self.Dal_VehicleModel = DAL_VehicleModel(
            session, vehicle_model, blacklist_model
        )
        self.NotificationModel = notification_model
        self.logger = logging.getLogger("vehicle_restriction")

    def get_conditions_and_restrictions_now(self, present_time):
        """
        Returns all conditions and restrictions
        """
        restrictions = (
            self.session.query(self.RestrictionModel)
            .filter(
                self.RestrictionModel.is_active == True,  # noqa
                self.RestrictionModel.start_time <= present_time,
                self.RestrictionModel.end_time >= present_time,
            )
            .all()
        )
        conditions = []
        for restriction in restrictions:
            conditions += restriction.aw_vehicle_restriction_condition_collection
        return restrictions, conditions

    def check_vehicles_in_restrictions_polygons(
        self, vehicles, condition, vehicle_list: list
    ):
        vehicles_id = [x.vehicle_id for x in vehicles]

        polygon_ids = [condition.polygon_id]
        params = {"vehicle_list": vehicles_id, "polygon_list": polygon_ids}
        with open(
            f"{settings.SQL_PATH}/vehicle_list_in_restriction_polygon.sql"
        ) as file:
            query = text(file.read())
            query = query.bindparams(
                bindparam("vehicle_list", expanding=True),
                bindparam("polygon_list", expanding=True),
            )
            vehicles_in_polygon = self.session.execute(query, params)
            vehicles_models = self.Dal_VehicleModel.get_vehicles_from_cursor(
                vehicles_in_polygon
            )
            vehicle_list.append(
                (
                    vehicles_models,
                    condition,
                )
            )

    def check_vehicles_out_restrictions_polygons(
        self, vehicles_filtered, condition, vehicles_set
    ):
        vehicles_id = [x.vehicle_id for x in vehicles_filtered]
        polygon_ids = [condition.polygon_id]
        patents = [condition.plate_pattern]
        params = {
            "vehicle_list": vehicles_id,
            "polygon_list": polygon_ids,
            "patent_list": patents,
        }
        with open(
            f"{settings.SQL_PATH}/vehicle_list_out_restriction_polygon.sql"
        ) as file:
            query = text(file.read())
            query = query.bindparams(
                bindparam("vehicle_list", expanding=True),
                bindparam("polygon_list", expanding=True),
                bindparam("patent_list", expanding=True),
            )
            vehicles_out_polygon = self.session.execute(query, params)
        sqlalchemy_vehicles = self.Dal_VehicleModel.get_vehicles_from_cursor(
            vehicles_out_polygon
        )
        for vehicle in sqlalchemy_vehicles:
            vehicles_set.add(vehicle)

    def get_actions_actions_from_restrictions(self, restrictions):
        restrictions_ids = [x.restriction_id for x in restrictions]
        actions = self.session.query(self.ActionModel).filter(
            self.ActionModel.restriction_id.in_(restrictions_ids)
        )
        return actions

    def get_template_name_by_id(self, id):
        name = (
            self.session.query(self.NotificationModel)
            .filter(self.NotificationModel.id == id)
            .first()
            .name
        )
        return name

    def get_template_id_by_actions(self, actions):
        template_id = (
            self.session.query(self.ActionModel)
            .filter_by(veh_rest_action_id=3)
            .first()
            .notification_id
        )
        return template_id
