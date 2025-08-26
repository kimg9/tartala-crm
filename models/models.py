import datetime
import enum

import sqlalchemy as db
from sqlalchemy import Table
from sqlalchemy.orm import relationship

from db_config.base import Base

users_permissions_association = Table(
    "users_permissions",
    Base.metadata,
    db.Column("user_id", db.ForeignKey("users.id"), primary_key=True),
    db.Column("permission_id", db.ForeignKey(
        "permissions.id"), primary_key=True),
)


class ResourceTypeEnum(enum.Enum):
    CONTRACT = "contract"
    EVENT = "event"
    CLIENT = "client"
    USER = "user"


class DepartmentEnum(enum.Enum):
    COMMERCIAL = "Département commercial"
    SUPPORT = "Département support"
    GESTION = "Département gestion"


class PermissionTypeEnum(enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class ContractStatusEnum(enum.Enum):
    SIGNED = "Signé"
    NOT_SIGNED = "Non signé"


class Resources(Base):
    # __abstract__ = True
    __tablename__ = "resources"
    __mapper_args__ = {"polymorphic_identity": "resources",
                       "polymorphic_on": "type"}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    creation_date = db.Column(
        db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"))
    modified_date = db.Column(
        db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("Users", backref="resources")


class Users(Base):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)
    department = db.Column(db.Enum(DepartmentEnum))
    permissions = relationship(
        "Permissions",
        secondary=users_permissions_association,
        back_populates="users",
        collection_class=set,
    )

    def __repr__(self):
        return f"User {self.name}"


class Permissions(Base):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    permission_type = db.Column(db.Enum(PermissionTypeEnum), nullable=False)
    resource_type = db.Column(db.Enum(ResourceTypeEnum), nullable=False)

    users = relationship(
        "Users",
        secondary=users_permissions_association,
        back_populates="permissions",
        collection_class=set,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "permission_type", "resource_type", name="ucstr_type_resource"
        ),
    )


class Clients(Resources):
    __tablename__ = "clients"
    __mapper_args__ = {"polymorphic_identity": "client"}

    id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String)
    telephone = db.Column(db.String)
    company_name = db.Column(db.String)

    events = relationship(
        "Events",
        back_populates="client",
        foreign_keys="Events.client_id",
        collection_class=set,
    )
    contracts = relationship(
        "Contracts",
        back_populates="client",
        foreign_keys="[Contracts.client_id]",
        collection_class=set,
    )


class Contracts(Resources):
    __tablename__ = "contracts"
    __mapper_args__ = {"polymorphic_identity": "contract"}

    id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)
    amount = db.Column(db.Integer)
    due_amount = db.Column(db.Integer)
    status = db.Column(db.Enum(ContractStatusEnum))
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    client = relationship(
        "Clients",
        back_populates="contracts",
        uselist=False,
        foreign_keys=[client_id],
        collection_class=set,
    )
    event = relationship(
        "Events",
        back_populates="contract",
        uselist=False,
        foreign_keys=[event_id],
        collection_class=set,
    )

    @classmethod
    def create(cls, session, user, **kwargs):
        contract = Contracts(**kwargs)
        contract.creation_date = datetime.datetime.now()
        contract.modified_date = datetime.datetime.now()
        contract.user = user
        session.add(contract)
        session.commit()
        return contract


class Events(Resources):
    __tablename__ = "events"
    __mapper_args__ = {"polymorphic_identity": "event"}

    id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    location = db.Column(db.Text)
    attendees = db.Column(db.Integer)
    notes = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

    client = relationship(
        "Clients",
        foreign_keys=[client_id],
        back_populates="events",
        uselist=False,
        collection_class=set,
    )
    contract = relationship(
        "Contracts",
        foreign_keys="[Contracts.event_id]",
        back_populates="event",
        uselist=False,
        collection_class=set,
    )

    @classmethod
    def create(cls, session, user, **kwargs):
        event = Events(**kwargs)
        event.creation_date = datetime.datetime.now()
        event.modified_date = datetime.datetime.now()
        event.user = user
        session.add(event)
        session.commit()
        return event
