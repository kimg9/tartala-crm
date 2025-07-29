from datetime import datetime

from db_config.connexion import session
from repositories.contracts.contract_repository import ContractRepository

contract_repo = ContractRepository(session)


class ContractApp:
    def create(self, **kwargs):
        kwargs["creation_date"] = datetime.now()
        kwargs["modified_date"] = datetime.now()

        return contract_repo.create_contract(**kwargs)
