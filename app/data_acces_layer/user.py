class DAL_UserModel:
    def __init__(self, session, user_model):
        self.session = session
        self.UserModel = user_model

    def get_user_by_id(self, user_id: int):
        return (
            self.session.query(self.UserModel)
            .filter(self.UserModel.user_id == user_id)
            .one()  # one() is for geting one object only
        )

    def get_users_by_ids(self, user_ids: list):
        return (
            self.session.query(self.UserModel)
            .filter(self.UserModel.user_id.in_(user_ids))
            .all()
        )
