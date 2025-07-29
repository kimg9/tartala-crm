from datetime import datetime

from db_config.connexion import session
from repositories.clients.client_repository import ClientRepository

client_repo = ClientRepository(session)


class ClientApp:
    def create(self, **kwargs):
        kwargs["creation_date"] = datetime.now()
        kwargs["modified_date"] = datetime.now()

        return client_repo.create_client(**kwargs)
