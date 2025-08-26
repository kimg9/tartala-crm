import enum
import random
import re
import readline
import string

import click

from models.models import ContractStatusEnum, DepartmentEnum


class BasicFilters(enum.Enum):
    ALL = "Tout voir"
    MINE = "Voir mes fiches"


def input_with_prefill(prompt, text):
    if not text:
        return input(prompt)

    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result


def number_input(prompt: str, text=None):
    while True:
        try:
            num = int(input_with_prefill(prompt, text))
            break
        except ValueError:
            print("Merci de n'entrer que des chiffres.")
    return num


def email_input(prompt: str, text=None):
    while True:
        email = input_with_prefill(prompt, text)
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, email):
            break
        else:
            print("Le format de cet email n'est pas valide.")
    return email


def random_password():
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(16))


def prompt_client(default: dict = None):
    full_name = click.prompt(
        "Nom complet",
        type=str,
        default=default["full_name"] if default else None
    )
    email = email_input("Email : ", text=default["email"] if default else None)
    telephone = click.prompt(
        "Téléphone",
        type=int,
        default=default["telephone"] if default else None
    )
    company_name = click.prompt(
        "Nom de l'entreprise",
        type=str,
        default=default["company_name"] if default else None
    )
    return {
        "full_name": full_name,
        "email": email,
        "telephone": telephone,
        "company_name": company_name,
    }


def prompt_event(default: dict = None):
    start = click.prompt(
        "Date de début de l'événement (doit être au format AAAA-MM-JJ)",
        type=click.DateTime(formats=["%Y-%m-%d"]),
        default=default["start"] if default else None
    )
    end = click.prompt(
        "Date de fin de l'événement (doit être au format AAAA-MM-JJ)",
        type=click.DateTime(formats=["%Y-%m-%d"]),
        default=default["end"] if default else None
    )
    location = click.prompt(
        "Localiation de l'évènement",
        type=str,
        default=default["location"] if default else None
    )
    attendees = click.prompt(
        "Nombre d'invités à l'événement",
        type=int,
        default=default["attendees"] if default else None
    )
    notes = click.prompt(
        "Notes",
        type=str,
        default=default["notes"] if default else None
    )
    client_id = click.prompt(
        "Id du client",
        type=int,
        default=default["client_id"] if default else None
    )
    return {
        "start": start,
        "end": end,
        "location": location,
        "attendees": attendees,
        "notes": notes,
        "client_id": client_id,
    }


def prompt_contract(default: dict = None):
    amount = click.prompt(
        "Montant du contrat",
        type=int,
        default=default["amount"] if default else None
    )
    due_amount = click.prompt(
        "Montant restant à payer",
        type=int,
        default=default["due_amount"] if default else None
    )
    status = ContractStatusEnum(click.prompt(
        "Status",
        type=click.Choice([e.value for e in ContractStatusEnum]),
        default=default["status"] if default else None
    ))
    client_id = click.prompt(
        "Id du client",
        type=int,
        default=default["client_id"] if default else None
    )
    event_id = click.prompt(
        "Id de l'événement",
        type=int,
        default=default["event_id"] if default else None
    )
    return {
        "amount": amount,
        "due_amount": due_amount,
        "status": status,
        "client_id": client_id,
        "event_id": event_id,
    }


def prompt_user(default: dict = None):
    name = click.prompt(
        "Nom",
        type=str,
        default=default["name"] if default else None
    )
    email = email_input("Email : ", text=default["email"] if default else None)
    username = click.prompt(
        "Nom d'utilisateur",
        type=str,
        default=default["username"] if default else None
    )
    password = ""
    if not default:
        password = click.prompt(
            "Mot de passe",
            type=str,
            default=random_password()
        )
    department = click.prompt(
        "Département",
        type=click.Choice([e.value for e in DepartmentEnum]),
        default=default["department"] if default else None
    )
    user_dict = {
        "name": name,
        "email": email,
        "username": username,
        "department": DepartmentEnum(department)
    }
    if password:
        user_dict["password"] = password
    return user_dict
