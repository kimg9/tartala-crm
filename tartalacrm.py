import getpass
import os
from datetime import date
from functools import wraps

import click
import jwt
from rich import box
from rich.console import Console
from rich.table import Table

from app.client_app import ClientApp
from app.contract_app import ContractApp
from app.event_app import EventApp
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
client_app = ClientApp()
event_app = EventApp()
contract_app = ContractApp()


@click.group()
def entry_point():
    pass


def authenticated_command(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        content = ""
        if os.path.exists(".tartalacrm_config"):
            with open(".tartalacrm_config", "r") as file:
                content = file.read().strip()

        if not content:
            raise click.ClickException(
                """
                Vous ne pouvez pas accéder à l'application sans JWT. 
                Merci d'en récupérer un à partir de la commande 'login'
                """
            )

        try:
            payload = jwt.decode(
                content,
                key=secret,
                algorithms=[
                    "HS256",
                ],
            )
        except jwt.ExpiredSignatureError as e:
            raise click.ClickException(f"Votre token est expiré: {e}")
        except jwt.InvalidSignatureError as e:
            raise click.ClickException(f"Votre token n'est pas valide: {e}")
        except jwt.DecodeError as e:
            raise click.ClickException(
                f"Votre token n'est pas dans un format valide: {e}")
        else:
            if not user_app.jwt_authentification(payload["id"], payload["username"]):
                raise click.ClickException("Utilisateur inconnu")
            else:
                print("Bienvenue dans TartalaCRM !")
                return f(*args, **kwargs)
    return wrapper


@entry_point.command()
def login():
    username = None
    while not username:
        username = input(
            "Veuillez renseigner votre nom d'utilisateur (ne peut être vide): "
        )
    password = getpass.getpass("Veuillez renseigner votre mot de passe: ")
    user = user_app.authentification(username, password)
    if not user:
        raise click.ClickException(
            "Désolé, votre utilisateur ou mot de passe n'est pas connu. Veuillez recommencer."
        )
    else:
        payload_data = {"id": user.id, "username": user.username}
        token = jwt.encode(payload=payload_data, key=secret)
        with open(".tartalacrm_config", "w+") as file:
            file.write(token)
        print("Connecté avec succès.")


@entry_point.command()
@authenticated_command
def populate():
    populator.populate()


@entry_point.command("list_items")
@click.argument("items", type=click.Choice(['clients', 'events', 'contracts']))
@authenticated_command
def list_items(items):
    now = f"Tableau généré le {date.today()}"
    table = Table(title=items.capitalize(), box=box.ROUNDED,
                  caption=now, caption_justify="left")

    match items:
        case "clients":
            clients = client_repo.list_all_clients()
            client_app.add_client_column_to_table(table, clients)
        case "events":
            events = event_repo.list_all_events()
            event_app.add_event_column_to_table(table, events)
        case "contracts":
            contracts = contract_repo.list_all_contracts()
            contract_app.add_contract_column_to_table(table, contracts)

    console = Console()
    console.print(table, justify="left")


if __name__ == "__main__":
    entry_point()
