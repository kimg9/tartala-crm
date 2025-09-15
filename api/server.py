import os
from typing import List

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from domain.client_app import ClientApp
from domain.contract_app import ContractApp
from domain.event_app import EventApp
from domain.user_app import UserApp

from .serializers import Client, Contract, Event, User, UserCreate

app = FastAPI(
    title='TartalaCRM',
    summary='API de TartalaCRM',
    description="""TartalaCRM est un CRM permettant de gérer clients, contrats et événements, 
    avec une gestion des rôles et une sécurité renforcée (SQLAlchemy, moindres privilèges, journalisation).
    Chaque département (commercial, support, gestion) dispose de droits spécifiques pour créer, modifier ou consulter les données.""",
    openapi_tags=[
        {
            'name': 'clients',
            'description': 'Gestion des clients'
        },
        {
            'name': 'contrats',
            'description': 'Gestion des contrats'
        },
        {
            'name': 'events',
            'description': 'Gestion des événements'
        },
        {
            'name': 'users',
            'description': 'Gestion des utilisateurs'
        },
    ]
)

event_domain = EventApp()
contract_domain = ContractApp()
client_domain = ClientApp()
user_domain = UserApp()
secret = os.environ.get("JWT_SECRET")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get_token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, key=secret, algorithms=["HS256"])
        user_id: int = payload.get("id")
        username: str = payload.get("username")
        if user_id is None or username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    else:
        return user_domain.get_by_id_and_username(user_id, username)

def get_event_or_404(id):
    event = event_domain.get_by_id(id)
    if not event:
        raise HTTPException(
            status_code=404, detail="Il n'existe aucun événement avec cet id.")
    return event


def get_client_or_404(id):
    client = client_domain.get_by_id(id)
    if not client:
        raise HTTPException(
            status_code=404, detail="Il n'existe aucun client avec cet id.")
    return client


def get_contract_or_404(id):
    contract = contract_domain.get_by_id(id)
    if not contract:
        raise HTTPException(
            status_code=404, detail="Il n'existe aucun contrat avec cet id.")
    return contract


def get_user_or_404(id):
    user = user_domain.get_by_id(id)
    if not user:
        raise HTTPException(
            status_code=404, detail="Il n'existe aucun utilisateur avec cet id.")
    return user


@app.post("/get_token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_domain.authentification(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d’utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload_data = {"id": user.id, "username": user.username}
    access_token = jwt.encode(payload=payload_data, key=secret)

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/events/", response_model=List[Event], tags=['events',])
def list_events(current_user: User = Depends(get_current_user)):
    return event_domain.list_all_events()


@app.get("/clients/", response_model=List[Client], tags=['clients',])
def list_clients(current_user: User = Depends(get_current_user)):
    return client_domain.list_all_clients()


@app.get("/contracts/", response_model=List[Contract], tags=['contrats',])
def list_contracts(current_user: User = Depends(get_current_user)):
    return contract_domain.list_all_contracts()


@app.get("/event/{id}", response_model=Event, tags=['events',])
def get_event(id: int, current_user: User = Depends(get_current_user)):
    return get_event_or_404(id)


@app.get("/client/{id}", response_model=Client, tags=['clients',])
def get_client(id: int, current_user: User = Depends(get_current_user)):
    return get_client_or_404(id)


@app.get("/contract/{id}", response_model=Contract, tags=['contrats',])
def get_contract(id: int, current_user: User = Depends(get_current_user)):
    return get_contract_or_404(id)


@app.get("/user/{id}", response_model=User, tags=['users',])
def get_user(id: int, current_user: User = Depends(get_current_user)):
    return get_user_or_404(id)


@app.post("/event", response_model=Event, tags=['events',])
def create_event(event: Event, current_user: User = Depends(get_current_user)):
    return event_domain.create(**event)


@app.post("/client", response_model=Client, tags=['clients',])
def create_client(client: Client, current_user: User = Depends(get_current_user)):
    return client_domain.create(**client)


@app.post("/contract", response_model=Contract, tags=['contrats',])
def create_contract(contract: Contract, current_user: User = Depends(get_current_user)):
    return contract_domain.create(**contract)


@app.post("/user", response_model=User, tags=['users',])
def create_user(user: UserCreate, current_user: User = Depends(get_current_user)):
    return user_domain.create(**user)


@app.put("/event/{id}", response_model=Event, tags=['events',])
def update_event(id: int, event: Event, current_user: User = Depends(get_current_user)):
    return event_domain.update(id=id, **event)


@app.put("/client/{id}", response_model=Client, tags=['clients',])
def update_client(id: int, client: Client, current_user: User = Depends(get_current_user)):
    return client_domain.update(id=id, **client)


@app.put("/contract/{id}", response_model=Contract, tags=['contrats',])
def update_contract(id: int, contract: Contract, current_user: User = Depends(get_current_user)):
    return contract_domain.update(id=id, **contract)


@app.put("/user/{id}", response_model=User, tags=['users',])
def update_user(id: int, user: User, current_user: User = Depends(get_current_user)):
    return user_domain.update(id=id ** user)


@app.delete("/event/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['users',])
def delete_event(id: int, current_user: User = Depends(get_current_user)):
    get_event_or_404(id)
    event_domain.delete(id)


@app.delete("/client/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['clients',])
def delete_client(id: int, current_user: User = Depends(get_current_user)):
    get_client_or_404(id)
    client_domain.delete(id)


@app.delete("/contract/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['contrats',])
def delete_contract(id: int, current_user: User = Depends(get_current_user)):
    get_contract_or_404(id)
    contract_domain.delete(id)


@app.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['users',])
def delete_user(id: int, current_user: User = Depends(get_current_user)):
    get_user_or_404(id)
    user_domain.delete(id)
