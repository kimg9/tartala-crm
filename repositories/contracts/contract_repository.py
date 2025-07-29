import sqlalchemy as db

from models.models import Contracts


class ContractRepository:
    def __init__(self, session):
        self.session = session

    def list_all_contracts(self):
        return self.session.execute(db.select(Contracts)).scalars().all()

    def create_contract(self, **kwargs):
        contract = Contracts(**kwargs)
        self.session.add(contract)
        self.session.commit()
        return contract
