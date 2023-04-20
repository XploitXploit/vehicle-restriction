import json
import requests
from datetime import datetime

from app.settings import settings
from app.data_acces_layer.restriction import DAL_RestrictionModel
from app.data_acces_layer.user import DAL_UserModel
from app.data_acces_layer.log import DAL_Log_Ongoing_User
from app.data_acces_layer.vehicle import DAL_VehicleModel


class Bll_MsNotification:
    def __init__(
        self,
        logger,
        session,
        session_log,
        restriction_model,
        vehicle_model,
        action_model,
        notification_model,
        user_model,
        Ongoing_model,
        blacklist_model,
    ) -> None:
        self.logger = logger
        self.OnGoingModel = Ongoing_model
        self.DAL_Restriction = DAL_RestrictionModel(
            session,
            restriction_model,
            vehicle_model,
            action_model,
            notification_model,
            blacklist_model,
        )
        self.DAL_User = DAL_UserModel(session, user_model)
        self.DalLogOngoingUser = DAL_Log_Ongoing_User(
            session_log, session, Ongoing_model, user_model
        )
        self.DAL_VehicleModel = DAL_VehicleModel(
            session, vehicle_model, blacklist_model
        )

    def send_notifications(
        self, users, actions, restriction_id, veh_rest_action_id, polygon_id
    ):
        try:
            self.logger.info("Sending notifications to MS")
            self.logger.info(f"Users: {[user.user_id for user in users]}")
            self.logger.debug(f"Type of users: {type(users)}")
            template_id = self.DAL_Restriction.get_template_id_by_actions(actions)
            template_name = self.DAL_Restriction.get_template_name_by_id(template_id)
            self.logger.info(f"template:{template_name}")
            for user in users:
                payload = json.dumps(
                    {
                        "userId": user.user_id,
                        "templateName": template_name,
                    }
                )
                self.logger.debug(f"payload send to ms-notifications:{payload}")
                response = requests.request(
                    "POST",
                    settings.MS_NOTIFICATION_URI,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                )
                vehicle_id = self.DAL_VehicleModel.get_vehicle_by_user_id(user.user_id)
                if response.status_code == 200:
                    log = self.OnGoingModel(
                        log_time=datetime.utcnow(),
                        restriction_id=restriction_id,
                        vehicle_id=vehicle_id.vehicle_id,
                        veh_rest_action_id=veh_rest_action_id,
                        polygon_id=polygon_id,
                        ongoing_user=user.user_id,
                    )
                    self.logger.info(
                        f"saving log for on_going user - {user.user_id} -: {log}"
                    )
                    self.DalLogOngoingUser.save_log(log=log)
                else:
                    self.logger.debug(
                        f"status code !=200 ---> ms_notification_response: {response.__dict__}"
                    )
        except Exception as e:
            self.logger.exception(e, exc_info=True)
        return response

    def get_auth_token(self):
        payload = json.dumps(
            {"username": settings.GOWGO_USER, "password": settings.GOWGO_PASSWORD}
        )
        headers = {"Content-Type": "application/json"}
        response = requests.request(
            "POST", settings.MS_LOGIN_URI, headers=headers, data=payload
        )
        self.logger.debug(f"ms_login_response: {response.__dict__}")
        return response.json()["token"]

    def get_ongoing_users_by_timespan(self, users_ids, time_span):
        try:
            users = self.DalLogOngoingUser.get_logs_of_users_ids_and_timespan(
                users_ids, time_span
            )
            self.logger.debug(
                f"get_ongoing_users_by_timespan:{[user.user_id for user in users]}{ 'None' if (length := len(users)) is None else length}"
            )
            users_ids = [x.user_id for x in users]
            self.logger.debug(f"get_ongoing_users_by_timespan:{users_ids}")
            return users_ids
        except Exception as e:
            self.logger.exception(e, exc_info=True)
