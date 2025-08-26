import sqlalchemy as db

from models.models import Contracts, ContractStatusEnum


class ContractRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id):
        pass_query = db.select(Contracts).where(Contracts.id == id)
        return self.session.execute(pass_query).scalar_one_or_none()

    def list_all_contracts(self):
        return self.session.execute(db.select(Contracts)).scalars().all()

    def list_user_contracts(self, user_id):
        return self.session.execute(db.select(Contracts).where(Contracts.user_id == user_id)).scalars().all()

    def list_all_unsigned_contracts(self):
        return self.session.execute(db.select(Contracts).where(Contracts.status == ContractStatusEnum.NOT_SIGNED)).scalars().all()

    def list_all_due_contracts(self):
        return self.session.execute(db.select(Contracts).where(Contracts.due_amount > 0)).scalars().all()

    def create_contract(self, **kwargs):
        contract = Contracts(**kwargs)
        self.session.add(contract)
        self.session.commit()
        return contract

    def save_to_db(self):
        self.session.commit()

    def delete(self, contract_id):
        contract = self.get_by_id(contract_id)
        if contract:
            self.session.delete(contract)
            self.save_to_db()
            return True
        return False
