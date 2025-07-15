import argparse
import getpass
import os

import jwt
from sqlalchemy.orm import sessionmaker

from db.connexion import engine
from models.models import Users
from populate import Populator

secret = os.environ.get("JWT_SECRET")


def login(session):
    username = None
    while not username:
        username = input(
            "Veuillez renseigner votre nom d'utilisateur (ne peut être vide):"
        )
    password = getpass.getpass("Veuillez renseigner votre mot de passe:")
    user = Users.authentification(username, password, session)
    if not user:
        print(
            "Désolé, votre utilisateur ou mot de passe n'est pas connu. Veuillez recommencer."
        )
    else:
        payload_data = {"id": user.id, "username": user.username}
        token = jwt.encode(payload=payload_data, key=secret)
        print(f"Voici votre JWT: {token}")


def populate(session):
    Populator(session).populate()


def authenticate(session):
    token = input("Veuillez renseigner votre jeton JWT: ")
    if not token:
        print(
            """
            Vous ne pouvez pas accéder à l'application sans JWT. 
            Merci d'en récupérer un à partir de la commande 'login'
            """
        )
        return False
    try:
        payload = jwt.decode(
            token,
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
        if not Users.jwt_authentification(payload["id"], payload["username"], session):
            print("Utilisateur inconnu")
            return False
        return True


def tartalacrm(session):
    if not authenticate(session):
        return

    print("Bienvenue dans TartalaCRM !")


if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    session = Session()

    parser = argparse.ArgumentParser(description="TartalaCRM")
    parser.add_argument(
        "command",
        choices=["login", "populate", "tartalacrm"],
        help="Commandes à exécuter",
    )
    args = parser.parse_args()

    globals()[args.command](session)
