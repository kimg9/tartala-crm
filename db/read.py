import sqlalchemy as db

from models.models import Clients, Contracts, Events, Users


def list_all_events(session):
    return session.execute(db.select(Events)).scalars().all()


def list_all_contracts(session):
    return session.execute(db.select(Contracts)).scalars().all()


def list_all_clients(session):
    return session.execute(db.select(Clients)).scalars().all()
