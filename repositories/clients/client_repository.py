import sqlalchemy as db

from models.models import Clients


class ClientRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id):
        pass_query = db.select(Clients).where(Clients.id == id)
        return self.session.execute(pass_query).scalar_one_or_none()

    def list_all_clients(self):
        return self.session.execute(db.select(Clients)).scalars().all()

    def create_client(self, **kwargs):
        client = Clients(**kwargs)
        self.session.add(client)
        self.session.commit()
        return client

    def save_to_db(self):
        self.session.commit()