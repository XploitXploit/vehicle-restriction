from collections import namedtuple
from datetime import datetime
import json
import time
import requests


from app.settings import settings
from app.utilities import week_intervals
from app.business_logic_layer.msnotification import Bll_MsNotification
from app.data_acces_layer.restriction import DAL_RestrictionModel
from app.data_acces_layer.log import DAL_Log
from app.data_acces_layer.user import DAL_UserModel
from app.data_acces_layer.vehicle import DAL_VehicleModel


class Bll_Restriction:
    def __init__(
        self,
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
        logger,
        NotificationModel,
        OnGoingLogModel,
        BlacklistModel,
    ) -> None:
        self.logger = logger
        self.session = session
        self.session_log = session_log
        self.VehicleModel = VehicleModel
        self.RestrictionModel = RestrictionModel
        self.ConditionModel = ConditionModel
        self.ActionModel = ActionModel
        self.TripModel = TripModel
        self.UserModel = UserModel
        self.LogModel = LogModel
        self.OnGoingLogModel = OnGoingLogModel
        self.bll_MsNotification = Bll_MsNotification(
            logger=logger,
            session=session,
            session_log=session_log,
            restriction_model=RestrictionModel,
            vehicle_model=VehicleModel,
            action_model=ActionModel,
            notification_model=NotificationModel,
            user_model=UserModel,
            Ongoing_model=OnGoingLogModel,
            blacklist_model=BlacklistModel,
        )
        self.dal_RestrictionModel = DAL_RestrictionModel(
            session=session,
            restriction_model=RestrictionModel,
            vehicle_model=VehicleModel,
            action_model=ActionModel,
            notification_model=NotificationModel,
            blacklist_model=BlacklistModel,
        )
        self.dal_LogModel = DAL_Log(session=session_log, LogModel=LogModel)
        self.dal_UserModel = DAL_UserModel(session=session, user_model=UserModel)
        self.dal_VehicleModel = DAL_VehicleModel(
            session=session, vehicle_model=VehicleModel, blacklist_model=BlacklistModel
        )
        self.out_vehicles_tuple = namedtuple(
            "out_vehicles_tuple", ["vehicles", "conditions"]
        )

    def check_vehicles_in_restrictions_polygons(self, vehicles_filtered):
        try:
            vehicles_sql = []
            for vehicles, condition in vehicles_filtered:
                self.dal_RestrictionModel.check_vehicles_in_restrictions_polygons(
                    vehicles, condition, vehicles_sql
                )
            return vehicles_sql
        except Exception as e:  # pragma: no cover
            self.logger.exception(e, exc_info=True)

    def check_vehicles_out_restrictions_poligons(self, vehicles_filtered, conditions):
        try:
            vehicles_set = set()
            for condition in conditions:
                self.dal_RestrictionModel.check_vehicles_out_restrictions_polygons(
                    vehicles_filtered, condition, vehicles_set
                )
            return vehicles_set
        except Exception as e:  # pragma: no cover
            self.logger.exception(e, exc_info=True)

    def make_actions_for_vehicles_in_restriction(
        self, vehicles_in_restriction, restrictions
    ):
        try:
            actions = self.dal_RestrictionModel.get_actions_actions_from_restrictions(
                restrictions
            )
            deactive_by_rodizio_action = actions.filter_by(
                pre_restriction_status_name="ACTIVE"  # CREATE A CONSTANT
            ).first()
            for vehicle_query, condition in vehicles_in_restriction:
                # TODO: add constants for the status
                vehicles_activated = self.dal_VehicleModel.filter_query_by_status(
                    vehicle_query, "ACTIVE"
                )
                vehicles_ongoing = self.dal_VehicleModel.filter_query_by_status(
                    vehicle_query, "ON_GOING"
                )
                self.logger.info(
                    f"make_actions_for_vehicles:"
                    f" vehicles_activated:{vehicles_activated}--vehicles_ongoing:{vehicles_ongoing}"
                )
                active_vehicles_ids = [x.vehicle_id for x in vehicles_activated]
                if len(active_vehicles_ids) > 0:
                    res = self.apply_action(
                        active_vehicles_ids,
                        deactive_by_rodizio_action.restriction_status_name,
                    )
                    if res.status_code == 200:
                        self.logger.info(
                            f"{len(active_vehicles_ids)} vehicles deactivated by rodizio"
                        )
                        logs = []
                        for vehicle_id in active_vehicles_ids:
                            logs.append(
                                self.LogModel(
                                    log_time=datetime.utcnow(),
                                    restriction_id=deactive_by_rodizio_action.restriction_id,
                                    vehicle_id=vehicle_id,
                                    veh_rest_action_id=deactive_by_rodizio_action.veh_rest_action_id,
                                    polygon_id=condition.polygon_id,
                                )
                            )
                        self.dal_LogModel.save_bulk_logs(logs)
                ongoing_action = actions.filter_by(
                    pre_restriction_status_name="ON_GOING"  # CREATE A CONSTANT
                ).first()
                ongoing_user_ids = [x.current_user_id for x in vehicles_ongoing]
                time_span_notification = ongoing_action.notification_time
                ongoing_users_by_timedelta = (
                    self.bll_MsNotification.get_ongoing_users_by_timespan(
                        ongoing_user_ids, time_span_notification
                    )
                )
                self.logger.debug(
                    f"after timespan method: {len(ongoing_users_by_timedelta)} vehicles are ongoing"
                )
                if len(ongoing_users_by_timedelta) > 0:
                    users = self.dal_UserModel.get_users_by_ids(
                        ongoing_users_by_timedelta
                    )
                    self.logger.debug(f"after_send_notification: {len(users)}")
                    if settings.TESTING:  # pragma: no cover
                        self.logger.info(f"Testing: user {users[0].user_id}")
                        users = list(
                            self.dal_UserModel.get_user_by_id(settings.TESTING_USER_ID)
                        )
                    self.bll_MsNotification.send_notifications(
                        users,
                        actions,
                        ongoing_action.restriction_id,
                        ongoing_action.veh_rest_action_id,
                        polygon_id=condition.polygon_id,
                    )
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    def make_actions_for_vehicles_out_restriction(
        self, vehicles_out_restriction, restrictions
    ):
        try:
            actions = self.dal_RestrictionModel.get_actions_actions_from_restrictions(
                restrictions
            )
            active_action = actions.filter_by(
                pre_restriction_status_name="DEACTIVE_BY_RODIZIO"
            ).first()

            deactive_vehicles_ids = [x.vehicle_id for x in vehicles_out_restriction]
            self.logger.info(f"vehicles_out_of_rodizio_ids:{deactive_vehicles_ids}")
            if len(deactive_vehicles_ids) > 0:
                res = self.apply_action(
                    deactive_vehicles_ids, active_action.restriction_status_name
                )

                if res.status_code == 200:
                    self.logger.info(
                        f"{len(deactive_vehicles_ids)} vehicles out of rodizio"
                    )
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    # This method has to go to a bll of msexternalcommon?
    def apply_action(self, vehicles_ids, new_status):
        try:
            payload = json.dumps(
                {
                    "vehicleIds": vehicles_ids,
                    "params": ["vehicle_current_status"],
                    "values": [new_status],
                }
            )
            headers = {
                "Authorization": settings.GOWGO_AUTH,
                "Content-Type": "application/json",
            }

            response = requests.request(
                "POST", settings.MS_MODIFY_STATUS_URI, headers=headers, data=payload
            )
            if response.status_code != 200:
                self.logger.error(response.text)
            else:
                self.logger.info(f"ms-external-common response: {response.__dict__}")
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            # TODO: send email to admin

        return response

    def get_conditions_date_intervals(self, conditions):
        try:
            filtered_conditions = []
            now_localized = week_intervals._localize_dt(
                datetime.utcnow(), "UTC", settings.TIME_ZONE
            )
            for condition in conditions:
                qm = week_intervals.quick_match(
                    condition.interval_definition, now_localized, settings.TIME_ZONE
                )
                if qm.is_contained:
                    self.logger.debug(f"{condition.interval_definition} is contained")
                    filtered_conditions.append(condition)
            return filtered_conditions
        except Exception as e:
            self.loger.exception(e, exc_info=True)

    def prefilter_vehicles(self, conditions, on_enter):
        try:
            filtered_conditions = self.get_conditions_date_intervals(conditions)
            vehicles_filtered = []
            if on_enter:
                if len(filtered_conditions) > 0:
                    for condition in filtered_conditions:
                        vehicles_filtered_1 = self.dal_VehicleModel.filter_vehicles_by_plate_pattern_and_status_list(
                                    condition, settings.VEHICLE_STATUS_FILTER
                                )
                        excluded_black_list = self.dal_VehicleModel.exclude_blacklist_models(vehicles_filtered_1)
                        vehicles_filtered.append(
                            (
                                excluded_black_list,
                                condition
                            )
                        )
                        self.logger.debug(f"prefilter_vehicles:{vehicles_filtered}")
            else:
                if len(filtered_conditions) > 0:
                    vehicles_filtered.append(
                        self.out_vehicles_tuple(
                            self.dal_VehicleModel.filter_vehicles_by_status(
                                "DEACTIVE_BY_RODIZIO"
                            ),
                            filtered_conditions,
                        )
                    )
                else:
                    vehicles_filtered = self.dal_VehicleModel.filter_vehicles_by_status(
                        "DEACTIVE_BY_RODIZIO"
                    )
            return vehicles_filtered, filtered_conditions
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    def get_conditions_and_restrictions(self):
        try:
            present_time = datetime.utcnow()
            return self.dal_RestrictionModel.get_conditions_and_restrictions_now(
                present_time
            )
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    def check_list_vehicle_in_restriction(self):
        try:
            restrictions, conditions = self.get_conditions_and_restrictions()
            vehicles_filtered, filtered_conditions = self.prefilter_vehicles(
                conditions, on_enter=True
            )
            for vehicles, _condition in vehicles_filtered:
                if len(vehicles) > 0:
                    vehicles_in_restriction = (
                        self.check_vehicles_in_restrictions_polygons(
                            vehicles_filtered=vehicles_filtered
                        )
                    )
                    self.make_actions_for_vehicles_in_restriction(
                        vehicles_in_restriction, restrictions
                    )
                    return self.prepare_response_for_vehicles_in_restriction(
                        vehicles_in_restriction
                    )
                else:
                    return []
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    def prepare_response_for_vehicles_in_restriction(self, vehicles_in_restriction):
        try:
            response = []
            if isinstance(vehicles_in_restriction[0], tuple):
                for tuple_vehicle_out_restriction in vehicles_in_restriction:
                    response.extend(tuple_vehicle_out_restriction)
            else:
                response += vehicles_in_restriction
            return response
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    def check_list_vehicle_out_restriction(self):
        try:
            restrictions, conditions = self.get_conditions_and_restrictions()
            vehicles_filtered, filtered_conditions = self.prefilter_vehicles(
                conditions, on_enter=False
            )
            # TODO: check new logic for on leave vehicles
            if len(filtered_conditions) == 0 and len(vehicles_filtered) > 0:
                vehicles_out_restriction = vehicles_filtered
                vehicles_ids = [x.vehicle_id for x in vehicles_out_restriction]
                self.apply_action(vehicles_ids, "ACTIVE")
            else:
                for tuple in vehicles_filtered:
                    vehicles_set = self.check_vehicles_out_restrictions_poligons(
                        vehicles_filtered=tuple.vehicles,
                        conditions=tuple.conditions,
                    )
                    if len(vehicles_set) > 0:
                        self.make_actions_for_vehicles_out_restriction(
                            vehicles_set, restrictions
                        )
                        return self.prepare_response_for_vehicles_out_restriction(
                            vehicles_set
                        )
                else:
                    return []
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    def prepare_response_for_vehicles_out_restriction(self, vehicles_out_restriction):
        try:
            response = []
            response += vehicles_out_restriction
            return response
        except Exception as e:
            self.logger.exception(e, exc_info=True)

    def run(self):
        try:
            start = time.time()
            vehicles_on_enter = self.check_list_vehicle_in_restriction()
            vehicles_on_leave = self.check_list_vehicle_out_restriction()
            end = time.time()
            self.logger.info(end - start)
            total = 0
            for list_of_vehicles in vehicles_on_enter:
                total += len(list_of_vehicles)
            self.logger.info(f"vehicles_on_enter: {total}")
            self.logger.info(f"vehicles_on_leave: {len(vehicles_on_leave)}")
        except Exception as e:
            self.logger.exception(e, exc_info=True)
