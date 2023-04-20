import logging
from datetime import datetime

from .user import DAL_UserModel

logger = logging.getLogger("vehicle_restriction")


class DAL_Log:
    """
    Data Access Layer for the Log
    """

    def __init__(self, session, LogModel):
        self.session = session
        self.LogModel = LogModel

    def get_logs(self, limit=None):
        """
        Returns all logs
        """
        logs = []
        if limit:
            logs = (
                self.session.query(self.LogModel)
                .order_by(self.LogModel.id.desc())
                .limit(limit)
                .all()
            )
        else:
            logs = (
                self.session.query(self.LogModel)
                .order_by(self.LogModel.id.desc())
                .all()
            )
        return logs

    def get_log_by_id(self, log_id):
        """
        Returns a log by id
        """
        return (
            self.session.query(self.LogModel).filter(self.LogModel.id == log_id).first()
        )

    def get_logs_by_vehicle_id(self, vehicle_id):
        """
        Returns all logs by vehicle_id
        """
        logs = (
            self.session.query(self.LogModel)
            .filter(self.LogModel.vehicle_id == vehicle_id)
            .order_by(self.LogModel.id.desc())
        ).all()
        return logs

    def save_log(self, log):
        """
        Saves a log
        """
        self.session.add(log)

    def save_bulk_logs(self, logs):
        """
        Saves a list of logs
        """
        self.session.bulk_save_objects(logs)


class DAL_Log_Ongoing_User:
    def __init__(self, session_log, session_awto, OnGoingLogModel, UserModel) -> None:
        self.session = session_log
        self.session_awto = session_awto
        self.OnGoingLogModel = OnGoingLogModel
        self.BllUser = DAL_UserModel(self.session_awto, UserModel)

    def get_logs(self, limit=None):
        """
        Returns all logs
        """
        logs = []
        if limit:
            logs = (
                self.session.query(self.OnGoingLogModel)
                .order_by(self.OnGoingLogModel.id.desc())
                .limit(limit)
                .all()
            )
        else:
            logs = (
                self.session.query(self.OnGoingLogModel)
                .order_by(self.OnGoingLogModel.id.desc())
                .all()
            )
        return logs

    def get_log_by_id(self, log_id):
        """
        Returns a log by id
        """
        return (
            self.session.query(self.OnGoingLogModel)
            .filter(self.OnGoingLogModel.id == log_id)
            .first()
        )

    def get_logs_by_user_id(self, user_id):
        """
        Returns all logs by vehicle_id
        """
        logs = (
            self.session.query(self.OnGoingLogModel)
            .filter(self.OnGoingLogModel.ongoing_user == user_id)
            .order_by(self.OnGoingLogModel.id.desc())
        ).all()
        return logs

    def get_logs_of_users_ids_and_timespan(self, users_ids, time_span):
        try:
            date = datetime.utcnow()
            users = []
            logger.info(f"get_logs_of_users_ids_and_timespan: {users_ids}")
            for user_id in users_ids:
                last_user_log = (
                    self.session.query(self.OnGoingLogModel)
                    .filter(
                        self.OnGoingLogModel.ongoing_user == user_id,
                    )
                    .order_by(self.OnGoingLogModel.id.desc())
                    .first()
                )
                if last_user_log:
                    time_diff = date - last_user_log.log_time
                    time_diff_hours = (time_diff.total_seconds()) / (60 * 60)
                    logger.info(f"time diff in hours:{time_diff_hours}")
                    if time_diff_hours >= time_span:
                        user = self.BllUser.get_user_by_id(user_id)
                        users.append(user)
                else:
                    user = self.BllUser.get_user_by_id(user_id)
                    users.append(user)
            logger.info(f"get_logs_of_users_ids_and_timespan:{len(users)}")
            return users
        except Exception as e:
            logger.exception(e, exc_info=True)

    def save_log(self, log):
        """
        Saves a log
        """
        try:
            self.session.add(log)
        except Exception as e:
            logger.info(e, exc_info=True)

    def save_bulk_logs(self, logs):
        """
        Saves a list of logs
        """
        self.session.bulk_save_objects(logs)
