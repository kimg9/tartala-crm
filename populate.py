import sqlalchemy as db

from db.connexion import engine
from models.models import (Clients, Contracts, DepartmentEnum, Events,
                           Permissions, Users)


class Populator:
    def __init__(self, session):
        self.session = session

    def _populate_permission_table(self):
        if not (
            self.session.query(Permissions)
            .filter_by(type="CREATE", resources=Clients)
            .one_or_none()
        ):
            with engine.connect() as conn:
                result = conn.execute(
                    db.insert(Permissions),
                    [
                        {"type": "CREATE", "resources": Clients},
                        {"type": "READ", "resources": Clients},
                        {"type": "UPDATE", "resources": Clients},
                        {"type": "DELETE", "resources": Clients},
                        {"type": "CREATE", "resources": Contracts},
                        {"type": "READ", "resources": Contracts},
                        {"type": "UPDATE", "resources": Contracts},
                        {"type": "DELETE", "resources": Contracts},
                        {"type": "CREATE", "resources": Events},
                        {"type": "READ", "resources": Events},
                        {"type": "UPDATE", "resources": Events},
                        {"type": "DELETE", "resources": Events},
                        {"type": "CREATE", "resources": Users},
                        {"type": "READ", "resources": Users},
                        {"type": "UPDATE", "resources": Users},
                        {"type": "DELETE", "resources": Users},
                    ],
                )
                conn.commit()
                return result

    def _populate_base_user(self):
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

    def populate(self):
        # self._populate_permission_table()
        self._populate_base_user()
