import argparse
import getpass
import os
from datetime import date

import jwt
from rich import box
from rich.console import Console
from rich.table import Table

from app.user_app import UserApp
from db_config.connexion import session
from populate import Populator
from repositories.clients.client_repository import ClientRepository
from repositories.contracts.contract_repository import ContractRepository
from repositories.events.event_repository import EventRepository

secret = os.environ.get("JWT_SECRET")
user_app = UserApp()
client_repo = ClientRepository(session)
contract_repo = ContractRepository(session)
event_repo = EventRepository(session)
populator = Populator(session)


def login():
    username = None
    while not username:
        username = input(
            "Veuillez renseigner votre nom d'utilisateur (ne peut être vide):"
        )
    password = getpass.getpass("Veuillez renseigner votre mot de passe:")
    user = user_app.authentification(username, password)
    if not user:
        print(
            "Désolé, votre utilisateur ou mot de passe n'est pas connu. Veuillez recommencer."
        )
    else:
        payload_data = {"id": user.id, "username": user.username}
        token = jwt.encode(payload=payload_data, key=secret)
        with open(".tartalacrm_config", "w+") as file:
            file.write(token)
        print("Connecté avec succès.")


def populate():
    populator.populate()


def authenticate():
    content = ""
    with open(".tartalacrm_config", "r") as file:
        content = file.read().strip()

    if not content:
        print(
            """
            Vous ne pouvez pas accéder à l'application sans JWT. 
            Merci d'en récupérer un à partir de la commande 'login'
            """
        )
        return False
    try:
        payload = jwt.decode(
            content,
            key=secret,
            algorithms=[
                "HS256",
            ],
        )
    except jwt.ExpiredSignatureError as e:
        print(f"Votre token est expiré: {e}")
    except jwt.InvalidSignatureError as e:
        print(f"Votre token n'est pas valide: {e}")
    except jwt.DecodeError as e:
        print(f"Votre token n'est pas dans un format valide: {e}")
    else:
        if not user_app.jwt_authentification(payload["id"], payload["username"]):
            print("Utilisateur inconnu")
        else:
            print("Bienvenue dans TartalaCRM !")
            return
    print(
        """
        Vous n'êtes pas authentifié. \n 
        Merci de récupérer un token JWT d'authentification à partir de la commande 'login'.
        """
    )


def list_clients():
    authenticate()
    now = f"Tableau généré le {date.today()}"
    table = Table(title="Clients", box=box.ROUNDED,
                  caption=now, caption_justify="left")

    clients = client_repo.list_all_clients()

    table.add_column("Nom complet", style="cyan")
    table.add_column("Email", style="green")
    table.add_column("Téléphone", style="green")
    table.add_column("Nom de l'entreprise", style="magenta")
    table.add_column("Date de création", style="deep_sky_blue3")
    table.add_column("Dernière mise à jour/contact", style="deep_sky_blue3")
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
            client.user.name,
        )

    console = Console()
    console.print(table, justify="left")


def list_contracts():
    authenticate()
    now = f"Tableau généré le {date.today()}"
    table = Table(
        title="Contrats",
        box=box.ROUNDED,
        caption=now,
        caption_justify="left",
        show_lines=True,
    )

    contracts = contract_repo.list_all_contracts()

    table.add_column("Identifiant", style="cyan")
    table.add_column("Nom du client", style="green")
    table.add_column("Contact du client", style="green")
    table.add_column("Contact commercial chez Epic Events",
                     style="deep_sky_blue3")
    table.add_column("Montant total", style="magenta")
    table.add_column("Restant à payer", style="magenta")
    table.add_column("Date de création", style="pale_violet_red1")
    table.add_column("Dernière mise à jour/contact", style="pale_violet_red1")
    table.add_column("Statut du contrat", style="turquoise2")

    for contract in contracts:
        table.add_row(
            f"{contract.id}",
            contract.client.full_name,
            f"{contract.client.email}\n{contract.client.telephone}",
            contract.user.name,
            f"{contract.amount} €",
            f"{contract.due_amount} €",
            contract.creation_date.strftime("%d/%m/%Y"),
            contract.modified_date.strftime("%d/%m/%Y"),
            contract.status,
        )

    console = Console()
    console.print(table, justify="left")


def list_events():
    authenticate()
    now = f"Tableau généré le {date.today()}"
    table = Table(
        title="Contrats",
        box=box.ROUNDED,
        caption=now,
        caption_justify="left",
        show_lines=True,
    )

    events = event_repo.list_all_events()

    table.add_column("Identifiant", style="cyan")
    table.add_column("Identifiant du contrat", style="light_salmon1")
    table.add_column("Nom du client", style="green")
    table.add_column("Contact du client", style="green")
    table.add_column("Date de début", style="magenta")
    table.add_column("Date de fin", style="magenta")
    table.add_column("Contact support chez Epic Events",
                     style="deep_sky_blue3")
    table.add_column("Localisation", style="turquoise2")
    table.add_column("Participants", style="turquoise2")
    table.add_column("Notes", style="pale_violet_red1")

    for event in events:
        table.add_row(
            f"{event.id}",
            f"{event.contract.id}" if event.contract else "",
            event.client.full_name,
            f"{event.client.email}\n{event.client.telephone}",
            event.start.strftime("%d/%m/%Y %H:%M"),
            event.end.strftime("%d/%m/%Y %H:%M"),
            event.user.name,
            event.location,
            f"{event.attendees}",
            event.notes,
        )

    console = Console()
    console.print(table, justify="left")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TartalaCRM")
    parser.add_argument(
        "command",
        choices=["login", "populate", "list_clients",
                 "list_contracts", "list_events"],
        help="Commandes à exécuter",
    )
    args = parser.parse_args()

    globals()[args.command]()
