from datetime import datetime

from db_config.connexion import session
from repositories.clients.client_repository import ClientRepository

client_repo = ClientRepository(session)


class ClientApp:
    def get_by_id(self, id):
        return client_repo.get_by_id(id)

    def create(self, **kwargs):
        kwargs["creation_date"] = datetime.now()
        kwargs["modified_date"] = datetime.now()

        return client_repo.create_client(**kwargs)

    def update(self, id, **kwargs):
        client = client_repo.get_by_id(id)
        if not client:
            return None

        forbidden_fields = ["id", "creation_date", "modified_date"]

        for key, value in kwargs.items():
            if key not in forbidden_fields:
                if hasattr(client, key):
                    setattr(client, key, value)

        kwargs["modified_date"] = datetime.now()

        client_repo.save_to_db()
        return client

    def delete(self, id):
        return client_repo.delete(id)

    @staticmethod
    def add_client_column_to_table(table):
        clients = client_repo.list_all_clients()

        table.add_column("Identifiant", style="cyan")
        table.add_column("Nom complet", style="cyan")
        table.add_column("Email", style="green")
        table.add_column("Téléphone", style="green")
        table.add_column("Nom de l'entreprise", style="magenta")
        table.add_column("Date de création", style="deep_sky_blue3")
        table.add_column("Dernière mise à jour/contact",
                         style="deep_sky_blue3")
        table.add_column("Contact commercial chez Epic Events",
                         style="deep_sky_blue3")

        for client in clients:
            table.add_row(
                f"{client.id}",
                client.full_name,
                client.email,
                client.telephone,
                client.company_name,
                client.creation_date.strftime("%d/%m/%Y"),
                client.modified_date.strftime("%d/%m/%Y"),
                client.user.name
            )

    def list_all_clients(self):
        return client_repo.list_all_clients()