import sqlalchemy as db

from db.connexion import engine
from models.models import (Clients, Contracts, DepartmentEnum, Events,
                           Permissions, PermissionTypeEnum, ResourceTypeEnum,
                           Users)


class Populator:
    def __init__(self, session):
        self.session = session

    def _populate_permission_table(self):
        if (
            not self.session.query(Permissions)
            .filter_by(
                permission_type=PermissionTypeEnum.CREATE,
                resource_type=ResourceTypeEnum.CLIENT,
            )
            .one_or_none()
        ):
            with engine.connect() as conn:
                result = conn.execute(
                    db.insert(Permissions),
                    [
                        {
                            "permission_type": PermissionTypeEnum.CREATE,
                            "resource_type": ResourceTypeEnum.CLIENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.READ,
                            "resource_type": ResourceTypeEnum.CLIENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.UPDATE,
                            "resource_type": ResourceTypeEnum.CLIENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.DELETE,
                            "resource_type": ResourceTypeEnum.CLIENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.CREATE,
                            "resource_type": ResourceTypeEnum.CONTRACT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.READ,
                            "resource_type": ResourceTypeEnum.CONTRACT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.UPDATE,
                            "resource_type": ResourceTypeEnum.CONTRACT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.DELETE,
                            "resource_type": ResourceTypeEnum.CONTRACT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.CREATE,
                            "resource_type": ResourceTypeEnum.EVENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.READ,
                            "resource_type": ResourceTypeEnum.EVENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.UPDATE,
                            "resource_type": ResourceTypeEnum.EVENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.DELETE,
                            "resource_type": ResourceTypeEnum.EVENT,
                        },
                        {
                            "permission_type": PermissionTypeEnum.CREATE,
                            "resource_type": ResourceTypeEnum.USER,
                        },
                        {
                            "permission_type": PermissionTypeEnum.READ,
                            "resource_type": ResourceTypeEnum.USER,
                        },
                        {
                            "permission_type": PermissionTypeEnum.UPDATE,
                            "resource_type": ResourceTypeEnum.USER,
                        },
                        {
                            "permission_type": PermissionTypeEnum.DELETE,
                            "resource_type": ResourceTypeEnum.USER,
                        },
                    ],
                )
                conn.commit()
                return result

    def _populate_root_user(self):
        user_select = db.select(Users).where(Users.username == "root")
        user = self.session.execute(user_select).scalars().all()
        if not user:
            Users.create(
                session=self.session,
                **{
                    "username": "root",
                    "password": "root",
                    "name": "root",
                    "email": "root@root.com",
                    "department": DepartmentEnum.SUPPORT,
                },
            )

    def _populate_existing_users_permissions(self):
        users_select = db.select(Users)
        users = self.session.execute(users_select).scalars().all()

        for user in users:
            user.set_permission()

        self.session.commit()

    def populate(self):
        self._populate_permission_table()
        self._populate_root_user()
        self._populate_existing_users_permissions()
