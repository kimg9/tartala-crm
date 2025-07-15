import enum

import sqlalchemy as db
from passlib.hash import argon2
from sqlalchemy import Table
from sqlalchemy.orm import relationship

from db.base import Base

users_permissions_association = Table(
    "users_permissions",
    Base.metadata,
    db.Column("user_id", db.ForeignKey("users.id"), primary_key=True),
    db.Column("permission_id", db.ForeignKey("permissions.id"), primary_key=True),
)


class Resources(Base):
    # __abstract__ = True
    __tablename__ = "resources"
    __mapper_args__ = {"polymorphic_identity": "resources", "polymorphic_on": "type"}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"))
    modified_date = db.Column(db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("Users", backref="resources")
    permissions = relationship("Permissions", back_populates="resource")


class DepartmentEnum(enum.Enum):
    COMMERCIAL = "Département commercial"
    SUPPORT = "Département support"
    GESTION = "Département gestion"


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
    )

    def __repr__(self):
        return f"User {self.name}"

    @classmethod
    def create(cls, session, **kwargs):
        user = Users(**kwargs)
        user.password = argon2.hash(user.password)
        session.add(user)
        session.commit()

    @staticmethod
    def authentification(username, password, session):
        pass_query = db.select(Users).where(Users.username == username)
        user = session.execute(pass_query).one_or_none()
        if user:
            if argon2.verify(password, user[0].password):
                return user[0]


class Permissions(Base):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)

    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    resource = relationship("Resources", back_populates="permissions")

    users = relationship(
        "Users",
        secondary=users_permissions_association,
        back_populates="permissions",
    )

    __table_args__ = (
        db.UniqueConstraint("type", "resource_id", name="ucstr_type_resource"),
    )


class Clients(Resources):
    __tablename__ = "clients"
    __mapper_args__ = {"polymorphic_identity": "client"}

    id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)
    information = db.Column(db.Text)
    full_name = db.Column(db.String)
    email = db.Column(db.String)
    telephone = db.Column(db.String)
    company_name = db.Column(db.String)

    events = relationship(
        "Events", back_populates="client", foreign_keys="Events.client_id"
    )
    contracts = relationship(
        "Contracts", back_populates="client", foreign_keys="[Contracts.client_id]"
    )


class Contracts(Resources):
    __tablename__ = "contracts"
    __mapper_args__ = {"polymorphic_identity": "contract"}

    id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)
    amount = db.Column(db.Integer)
    due_amount = db.Column(db.Integer)
    status = db.Column(db.String)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    client = relationship(
        "Clients", back_populates="contracts", uselist=False, foreign_keys=[client_id]
    )
    event = relationship(
        "Events", back_populates="contract", uselist=False, foreign_keys=[event_id]
    )


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
        "Clients", foreign_keys=[client_id], back_populates="events", uselist=False
    )
    contract = relationship(
        "Contracts",
        foreign_keys="[Contracts.event_id]",
        back_populates="event",
        uselist=False,
    )
