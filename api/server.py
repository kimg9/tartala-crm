from fastapi import FastAPI, HTTPException, status

from domain.client_app import ClientApp
from domain.contract_app import ContractApp
from domain.event_app import EventApp
from domain.user_app import UserApp
from .serializers import Client, Contract, Event, User, UserCreate
from typing import List

app = FastAPI(
    title='TartalaCRM',
    summary='API de TartalaCRM',
    description="""TartalaCRM est un CRM permettant de gérer clients, contrats et événements, 
    avec une gestion des rôles et une sécurité renforcée (SQLAlchemy, moindres privilèges, journalisation). \n
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


@app.get("/events/", response_model=List[Event], tags=['events',])
def list_events():
    return event_domain.list_all_events()


@app.get("/clients/", response_model=List[Client], tags=['clients',])
def list_clients():
    return client_domain.list_all_clients()


@app.get("/contracts/", response_model=List[Contract], tags=['contrats',])
def list_contracts():
    return contract_domain.list_all_contracts()


@app.get("/event/{id}", response_model=Event, tags=['events',])
def get_event(id: int):
    return get_event_or_404(id)


@app.get("/client/{id}", response_model=Client, tags=['clients',])
def get_client(id: int):
    return get_client_or_404(id)


@app.get("/contract/{id}", response_model=Contract, tags=['contrats',])
def get_contract(id: int):
    return get_contract_or_404(id)


@app.get("/user/{id}", response_model=User, tags=['users',])
def get_user(id: int):
    return get_user_or_404(id)


@app.post("/event", response_model=Event, tags=['events',])
def create_event(event: Event):
    return event_domain.create(**event)


@app.post("/client", response_model=Client, tags=['clients',])
def create_client(client: Client):
    return client_domain.create(**client)


@app.post("/contract", response_model=Contract, tags=['contrats',])
def create_contract(contract: Contract):
    return contract_domain.create(**contract)


@app.post("/user", response_model=User, tags=['users',])
def create_user(user: UserCreate):
    return user_domain.create(**user)


@app.put("/event/{id}", response_model=Event, tags=['events',])
def update_event(id: int, event: Event):
    return event_domain.update(id=id, **event)


@app.put("/client/{id}", response_model=Client, tags=['clients',])
def update_client(id: int, client: Client):
    return client_domain.update(id=id, **client)


@app.put("/contract/{id}", response_model=Contract, tags=['contrats',])
def update_contract(id: int, contract: Contract):
    return contract_domain.update(id=id, **contract)


@app.put("/user/{id}", response_model=User, tags=['users',])
def update_user(id: int, user: User):
    return user_domain.update(id=id ** user)


@app.delete("/event/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['users',])
def delete_event(id: int):
    get_event_or_404(id)
    event_domain.delete(id)


@app.delete("/client/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['clients',])
def delete_client(id: int):
    get_client_or_404(id)
    client_domain.delete(id)


@app.delete("/contract/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['contrats',])
def delete_contract(id: int):
    get_contract_or_404(id)
    contract_domain.delete(id)


@app.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=['users',])
def delete_user(id: int):
    get_user_or_404(id)
    user_domain.delete(id)
