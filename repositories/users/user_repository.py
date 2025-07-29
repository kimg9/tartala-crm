import sqlalchemy as db

from models.models import Permissions, Users


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_username(self, username):
        pass_query = db.select(Users).where(Users.username == username)
        user = self.session.execute(pass_query).one_or_none()
        if user:
            user = user[0]
        return user

    def get_by_id_and_username(self, id, username):
        pass_query = db.select(Users).where(Users.id == id, Users.username == username)
        return self.session.execute(pass_query).one_or_none()

    def bulk_update_permissions(self, user: Users, permissions_list: list):
        conds = [
            (Permissions.permission_type == perm_type)
            & (Permissions.resource_type == resource_type)
            for perm_type, resource_type in permissions_list
        ]
        query = db.select(Permissions).where(db.or_(*conds))
        perm_list = self.session.execute(query).scalars().all()
        user.permissions.update(perm_list)
        self.session.commit()

    def create_user(self, **kwargs):
        user = Users(**kwargs)
        self.session.add(user)
        self.session.commit()
        return user
