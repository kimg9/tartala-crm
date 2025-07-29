import sqlalchemy as db

from models.models import Clients


class ClientRepository:
    def __init__(self, session):
        self.session = session
        
    def list_all_clients(self):
        return self.session.execute(db.select(Clients)).scalars().all()

    def create_client(self, **kwargs):
        client = Clients(**kwargs)
        self.session.add(client)
        self.session.commit()
        return client