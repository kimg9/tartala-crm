from datetime import datetime

from db_config.connexion import session
from repositories.clients.client_repository import ClientRepository

client_repo = ClientRepository(session)


class ClientApp:
    def create(self, **kwargs):
        kwargs["creation_date"] = datetime.now()
        kwargs["modified_date"] = datetime.now()

        return client_repo.create_client(**kwargs)

    @staticmethod
    def add_client_column_to_table(table):
        clients = client_repo.list_all_clients()
        
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
                client.full_name,
                client.email,
                client.telephone,
                client.company_name,
                client.creation_date.strftime("%d/%m/%Y"),
                client.modified_date.strftime("%d/%m/%Y"),
            )
