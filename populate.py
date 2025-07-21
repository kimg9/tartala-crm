from datetime import datetime

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

    def _populate_users_test_data(self):
        user_select = db.select(Users).where(Users.username == "support")
        user = self.session.execute(user_select).scalars().all()
        if not user:
            Users.create(
                session=self.session,
                **{
                    "username": "support",
                    "password": "support",
                    "name": "support",
                    "email": "support@support.com",
                    "department": DepartmentEnum.SUPPORT,
                },
            )

        user_select = db.select(Users).where(Users.username == "commercial")
        user = self.session.execute(user_select).scalars().all()
        if not user:
            Users.create(
                session=self.session,
                **{
                    "username": "commercial",
                    "password": "commercial",
                    "name": "commercial",
                    "email": "commercial@commercial.com",
                    "department": DepartmentEnum.COMMERCIAL,
                },
            )

        user_select = db.select(Users).where(Users.username == "gestion")
        user = self.session.execute(user_select).scalars().all()
        if not user:
            Users.create(
                session=self.session,
                **{
                    "username": "gestion",
                    "password": "gestion",
                    "name": "gestion",
                    "email": "gestion@gestion.com",
                    "department": DepartmentEnum.GESTION,
                },
            )

    def _populate_existing_users_permissions(self):
        users_select = db.select(Users)
        users = self.session.execute(users_select).scalars().all()

        for user in users:
            user.set_permission()

        self.session.commit()

    def _populate_test_data(self):
        user_select = db.select(Users).where(Users.username == "commercial")
        user = self.session.execute(user_select).scalars().one_or_none()

        client_select = db.select(Clients).where(Clients.full_name == "Kevin Casey")
        client = self.session.execute(client_select).scalars().all()

        if not client:
            Clients.create(
                session=self.session,
                **{
                    "full_name": "Kevin Casey",
                    "email": "kevin@startup.io",
                    "telephone": "+678 123 456 78",
                    "company_name": "Cool Startup LLC",
                    "user": user,
                },
            )

        client_select = db.select(Clients).where(Clients.full_name == "John Ouick")
        client = self.session.execute(client_select).scalars().all()
        created_client = Clients()

        if not client:
            created_client = Clients.create(
                session=self.session,
                **{
                    "full_name": "John Ouick",
                    "email": "john.ouick@gmail.com",
                    "telephone": "+1 234 567 8901",
                    "company_name": "AWESOME Startup LLC",
                    "user": user,
                },
            )

        contract_select = db.select(Contracts).where(
            Contracts.amount == 1000, Contracts.client_id == created_client.id
        )
        contract = self.session.execute(contract_select).scalars().all()
        created_contract = Contracts()

        if not contract:
            created_contract = Contracts.create(
                session=self.session,
                **{
                    "amount": 1000,
                    "due_amount": 500,
                    "status": "Signé",
                    "client_id": created_client.id,
                    "client": created_client,
                    "user": user,
                },
            )

        user_select = db.select(Users).where(Users.username == "support")
        user = self.session.execute(user_select).scalars().one_or_none()

        event_select = db.select(Events).where(
            Events.location == "53 rue du Château, 41120 Candé-sur-Beuvron, France"
        )
        event = self.session.execute(event_select).scalars().all()

        if not event:
            Events.create(
                session=self.session,
                **{
                    "start": datetime(year=2023, month=6, day=4, hour=13),
                    "end": datetime(year=2023, month=6, day=5, hour=2),
                    "client_id": created_client.id,
                    "client": created_client,
                    "contract": created_contract,
                    "location": "53 rue du Château, 41120 Candé-sur-Beuvron, France",
                    "attendees": 75,
                    "notes": "Wedding starts at 3PM by the river. \n Catering is organized, reception starts at 5PM.\n Kate needs to organize the DJ for after party.",
                    "user": user,
                },
            )

    def populate(self):
        self._populate_permission_table()
        self._populate_users_test_data()
        self._populate_existing_users_permissions()
        self._populate_test_data()
