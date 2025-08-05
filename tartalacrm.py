import getpass
import os
from datetime import date
from functools import wraps

import click
import jwt
from rich import box
from rich.console import Console
from rich.table import Table

from domain.client_app import ClientApp
from domain.contract_app import ContractApp
from domain.event_app import EventApp
from domain.user_app import UserApp
from db_config.connexion import session
from populate import Populator
import utils as utils

secret = os.environ.get("JWT_SECRET")
populator = Populator(session)
user_app = UserApp()
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
                Merci d'utiliser la commande 'login' pour vous connecter.
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
        except jwt.ExpiredSignatureError:
            raise click.ClickException(
                f"Votre token est expiré. Merci d'utiliser la commande 'login' pour vous connecter.")
        except jwt.InvalidSignatureError:
            raise click.ClickException(
                f"Votre token n'est pas valide. Merci d'utiliser la commande 'login' pour vous connecter.")
        except jwt.DecodeError:
            raise click.ClickException(
                f"Votre token n'est pas dans un format valide. Merci d'utiliser la commande 'login' pour vous connecter.")
        else:
            user = user_app.jwt_authentification(
                payload["id"], payload["username"])
            if not user:
                raise click.ClickException("Utilisateur inconnu")
            else:
                print("Bienvenue dans TartalaCRM !")
                return f(*args, **kwargs, user=user)
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


@entry_point.command("list_items")
@click.argument("items", type=click.Choice(['clients', 'events', 'contracts']))
@authenticated_command
def list_items(items, user):
    if not user:
        raise click.ClickException("Utilisateur inconnu")
    now = f"Tableau généré le {date.today()}"
    table = Table(title=items.capitalize(), box=box.ROUNDED,
                  caption=now, caption_justify="left")

    match items:
        case "clients":
            client_app.add_client_column_to_table(table)
        case "events":
            event_app.add_event_column_to_table(table)
        case "contracts":
            contract_app.add_contract_column_to_table(table)

    console = Console()
    console.print(table, justify="left")


@entry_point.command("create_item")
@click.argument("item_type", type=click.Choice(['client', 'event', 'contract']))
@authenticated_command
def create_item(item_type, user):
    match item_type:
        case "client":
            if not user_app.has_permission(user=user, resource_type="client", permission_type="create"):
                print("Vous n'êtes pas autorisé à créer des clients.")
                return

            client_dict = utils.prompt_client()
            client_dict["user"] = user
            client = client_app.create(**client_dict)

            print(
                f"Vous avez réussi à créer le client (id du client : {client.id}).")

        case "event":
            if not user_app.has_permission(user=user, resource_type="event", permission_type="create"):
                print("Vous n'êtes pas autorisé à créer des événements.")
                return

            event_dict = utils.prompt_event()
            client_dict["user"] = user
            event = event_app.create(**event_dict)

            print(
                f"Vous avez réussi à créer l'événement (id de l'événement : {event.id})")
        case "contract":
            if not user_app.has_permission(user=user, resource_type="contract", permission_type="create"):
                print("Vous n'êtes pas autorisé à créer des contracts.")
                return

            contract_dict = utils.prompt_contract()
            client_dict["user"] = user
            contract = contract_app.create(**contract_dict)

            print(
                f"Vous avez réussi à créer l'événement (id du contrat : {contract.id})")


@entry_point.command("update_item")
@click.argument("item_type", type=click.Choice(['client', 'event', 'contract']))
@click.argument("item_id", type=int)
@authenticated_command
def update_item(item_type, item_id, user):
    match item_type:
        case "client":
            if not user_app.has_permission(user=user, resource_type="client", permission_type="update"):
                print("Vous n'êtes pas autorisé à modifier des clients.")
                return

            client = client_app.get_by_id(item_id)
            client_dict = {
                "full_name": client.full_name,
                "email": client.email,
                "telephone": client.telephone,
                "company_name": client.company_name,
            }
            updated_client_dict = utils.prompt_client(default=client_dict)
            client = client_app.update(id=item_id, **updated_client_dict)

            print(
                f"Vous avez réussi à mettre à jour le client (id du client : {client.id}).")

        case "event":
            if not user_app.has_permission(user=user, resource_type="event", permission_type="update"):
                print("Vous n'êtes pas autorisé à modifier des événements.")
                return

            event = event_app.get_by_id(item_id)
            event_dict = {
                "start": event.start,
                "end": event.end,
                "location": event.location,
                "attendees": event.attendees,
                "notes": event.notes,
                "client_id": event.client_id,
            }
            updated_event_dict = utils.prompt_event(default=event_dict)
            event = event_app.update(id=item_id, **updated_event_dict)

            print(
                f"Vous avez réussi à mettre à jour l'événement (id de l'événement : {event.id})")
        case "contract":
            if not user_app.has_permission(user=user, resource_type="contract", permission_type="update"):
                print("Vous n'êtes pas autorisé à modifier des contracts.")
                return

            contract_dict = utils.prompt_contract()
            contract = contract_app.update(id=item_id, **contract_dict)

            print(
                f"Vous avez réussi à mettre à jour l'événement (id du contrat : {contract.id})")


# TODO: remove after dev phase is over
@entry_point.command()
def populate():
    populator.populate()


if __name__ == "__main__":
    entry_point()
