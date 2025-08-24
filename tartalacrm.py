import getpass
import os
from datetime import date
from functools import wraps

import click
import jwt
from rich import box
from rich.console import Console
from rich.table import Table

import utils as utils
from db_config.connexion import session
from domain.client_app import ClientApp
from domain.contract_app import ContractApp
from domain.event_app import EventApp
from domain.user_app import UserApp
from populate import Populator

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
@click.argument("item_type", type=click.Choice(['client', 'event', 'contract', 'user']))
@authenticated_command
def create_item(item_type, user):
    if not user_app.has_permission(user=user, resource_type=item_type, permission_type="create"):
        print("Vous n'êtes pas autorisé à créer cette ressource.")
        return

    match item_type:
        case "user":
            user_dict = utils.prompt_user()
            user = user_app.create(**user_dict)
            print(f"Utilisateur {user.id} créé avec succès.")
        case "client":
            client_dict = utils.prompt_client()
            client_dict["user"] = user
            client = client_app.create(**client_dict)
            print(f"Client {client.id} créé avec succès.")
        case "event":
            event_dict = utils.prompt_event()
            client_dict["user"] = user
            event = event_app.create(**event_dict)
            print(f"Evénement {event.id} créé avec succès.")
        case "contract":
            contract_dict = utils.prompt_contract()
            client = client_app.get_by_id(contract_dict["client_id"])
            if not client.user_id == user.id:
                print("Vous n'êtes pas autorisé à créer un contrat pour un client dont vous n'êtes pas responsables.")
                return
            client_dict["user"] = user
            contract = contract_app.create(**contract_dict)
            print(f"Contrat {contract.id} créé avec succès")


@entry_point.command("update_item")
@click.argument("item_type", type=click.Choice(['client', 'event', 'contract', 'user']))
@click.argument("item_id", type=int)
@authenticated_command
def update_item(item_type, item_id, user):
    if not user_app.has_permission(user=user, resource_type=item_type, permission_type="create"):
        print("Vous n'êtes pas autorisé à modifier cette ressource.")
        return

    match item_type:
        case "user":
            user = user_app.get_by_id(item_id)
            if not user:
                print(f"L'utilisateur {item_id} n'existe pas.")
                return
            user_dict = {
                "name": user.name,
                "email": user.email,
                "username": user.username,
                "department": user.department.value
            }
            updated_user_dict = utils.prompt_user(user_dict)
            user = user_app.update(id=item_id, **updated_user_dict)
            print(f"Utilisateur {user.id} modifié avec succès.")

        case "client":
            client = client_app.get_by_id(item_id)
            if not client:
                print(f"Le client {item_id} n'existe pas.")
                return
            if not client.user_id == user.id:
                print(f"Vous n'êtes pas le propriétaire de la fiche client {item_id}.")
                return
            client_dict = {
                "full_name": client.full_name,
                "email": client.email,
                "telephone": client.telephone,
                "company_name": client.company_name,
            }
            updated_client_dict = utils.prompt_client(default=client_dict)
            client = client_app.update(id=item_id, **updated_client_dict)
            print(f"Client {client.id} modifié avec succès.")

        case "event":
            event = event_app.get_by_id(item_id)
            if not event:
                print(f"L'événement {item_id} n'existe pas.")
                return
            if not event.user_id == user.id:
                print(f"Vous n'êtes pas le propriétaire de la fiche événement {item_id}.")
                return
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
            print(f"Evénement {event.id} modifié avec succès.")

        case "contract":
            contract = contract_app.get_by_id(item_id)
            if not contract:
                print(f"Le contrat {item_id} n'existe pas.")
                return
            contract_dict = {
                "amount": contract.amount,
                "due_amount": contract.due_amount,
                "status": contract.status,
                "client_id": contract.client_id,
                "event_id": contract.event_id,
            }
            updated_contract_dict = utils.prompt_contract(contract_dict)
            contract = contract_app.update(id=item_id, **updated_contract_dict)
            print(f"Contrat {contract.id} modifié avec succès")


@entry_point.command("delete_item")
@click.argument("item_type", type=click.Choice(['client', 'event', 'contract', 'user']))
@click.argument("item_id", type=int)
@authenticated_command
def delete_item(item_type, item_id, user):
    if not user_app.has_permission(user=user, resource_type=item_type, permission_type="delete"):
        print("Vous n'êtes pas autorisé à supprimer cette ressource.")
        return

    match item_type:
        case "user":
            to_del_user = user_app.get_by_id(item_id)
            if not to_del_user:
                print(f"L'utilisateur {item_id} n'existe pas.")
                return
            if not to_del_user.user_id == user.id:
                print(f"Vous ne pouvez pas supprimer une ressource dont vous n'êtes pas propriétaire.")
                return
            if click.confirm(f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user.id} {user.username} ?", default=False):
                deleted = user_app.delete(item_id)
                if deleted:
                    print("Utilisateur supprimé avec succès.")
        case "client":
            client = client_app.get_by_id(item_id)
            if not client:
                print(f"Le client {item_id} n'existe pas.")
                return
            if not client.user_id == user.id:
                print(f"Vous ne pouvez pas supprimer une ressource dont vous n'êtes pas propriétaire.")
                return
            if click.confirm(f"Êtes-vous sûr de vouloir supprimer le client {client.id} {client.full_name} ?", default=False):
                deleted = client_app.delete(item_id)
                if deleted:
                    print("Client supprimé avec succès.")
        case "event":
            event = event_app.get_by_id(item_id)
            if not event:
                print(f"L'événement {item_id} n'existe pas.")
                return
            if not event.user_id == user.id:
                print(f"Vous ne pouvez pas supprimer une ressource dont vous n'êtes pas propriétaire.")
                return
            if click.confirm(f"Êtes-vous sûr de vouloir supprimer l'événement {event.id} qui se déroule à {event.location} ?", default=False):
                deleted = event_app.delete(item_id)
                if deleted:
                    print("Evénement supprimé avec succès.")
        case "contract":
            contract = contract_app.get_by_id(item_id)
            if not contract:
                print(f"Le contrat {item_id} n'existe pas.")
                return
            if not contract.user_id == user.id:
                print(f"Vous ne pouvez pas supprimer une ressource dont vous n'êtes pas propriétaire.")
                return
            if click.confirm(f"Êtes-vous sûr de vouloir supprimer l'événement {contract.id} qui se déroule à {contract.location} ?", default=False):
                deleted = contract_app.delete(item_id)
                if deleted:
                    print("Contrat supprimé avec succès.")


# TODO: remove after dev phase is over
@entry_point.command()
def populate():
    populator.populate()


if __name__ == "__main__":
    entry_point()
