from typing import List
from passlib.hash import argon2
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Table

from db.base import Base
from db.connexion import session

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    department = Column(String)
    user_permission: Mapped["Permissions"] = relationship("permissions", back_populates="users")
    user_clients: Mapped[List["Clients"]] = relationship("clients", back_populates="user")
    user_contracts: Mapped[List["Contracts"]] = relationship("contracts", back_populates="user")

    def __repr__(self):
        return f"User {self.name}"

    @classmethod
    def create(cls, **kwargs):
        user = Users(**kwargs)
        user.password = argon2.hash(user.password)
        session.add(user)
        session.commit()


class Permissions(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    type = Column(String) #read, update, delete, create
    filter_type = Column(String)
    user_permissions: Mapped[List["Users"]] = relationship("users", back_populates="permissions")
    resources: Mapped["Resources"]= relationship("Resources", back_populates="permissions")


class Resources(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    creation_date = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    modified_date = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    user_id = Column(Integer, ForeignKey("users.id"))

    @declared_attr
    def user_contact(cls) -> Mapped["Users"]:
        return relationship("users", back_populates="contracts")

    @declared_attr
    def permissions(cls) -> Mapped[List["Permissions"]] :
        return relationship("permissions", back_populates="resources")


class Clients(Resources):
    __tablename__ = "clients"
    
    information = Column(Text)
    full_name = Column(String)
    email = Column(String)
    telephone = Column(String)
    company_name = Column(String)
    events: Mapped["Events"] = relationship("events", back_populates="clients")


class Contracts(Resources):
    __tablename__ = "contracts"
    
    event_id: Mapped["Events"] = relationship("events", back_populates="contract")
    client_name: Mapped["Clients"] = relationship("clients", back_populates="contract")
    amount = Column(Integer)
    due_amount = Column(Integer)
    status = Column(String)


class Events(Resources):
    __tablename__ = "events"
    
    contract_id: Mapped["Contracts"] = relationship("contracts", back_populates="event")
    client_name: Mapped["Clients"] = relationship("clients", back_populates="event")
    start = Column(DateTime)
    end = Column(DateTime)
    location = Column(Text)
    attendees = Column(Integer)
    notes = Column(Text)


users_permissions_association =  Table(
    "users_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True)
)

users_clients_association =  Table(
    "users_clients",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("client_id", ForeignKey("clients.id"), primary_key=True)
)

users_contracts_association =  Table(
    "users_contracts",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("contract_id", ForeignKey("contracts.id"), primary_key=True)
)

users_events_association =  Table(
    "users_events",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("event_id", ForeignKey("events.id"), primary_key=True)
)

clients_events_association =  Table(
    "clients_events",
    Base.metadata,
    Column("client_id", ForeignKey("clients.id"), primary_key=True),
    Column("event_id", ForeignKey("events.id"), primary_key=True)
)

events_contracts_association =  Table(
    "events_contracts",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("contract_id", ForeignKey("contracts.id"), primary_key=True)
)
