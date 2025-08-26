import enum
from datetime import datetime

from db_config.connexion import session
from repositories.contracts.contract_repository import ContractRepository
from utils import BasicFilters

contract_repo = ContractRepository(session)


class ContractApp:
    class ContractFilters(enum.Enum):
        UNSIGNED = "Contrats non signés"
        DUE = "Contrats non soldés"

    def get_by_id(self, id):
        return contract_repo.get_by_id(id)

    def create(self, **kwargs):
        kwargs["creation_date"] = datetime.now()
        kwargs["modified_date"] = datetime.now()

        return contract_repo.create_contract(**kwargs)

    def update(self, id, **kwargs):
        contract = contract_repo.get_by_id(id)
        if not contract:
            return None

        forbidden_fields = ["id", "creation_date", "modified_date"]

        for key, value in kwargs.items():
            if key not in forbidden_fields:
                if hasattr(contract, key):
                    setattr(contract, key, value)

        kwargs["modified_date"] = datetime.now()

        contract_repo.save_to_db()
        return contract

    def delete(self, id):
        return contract_repo.delete(id)

    def add_contract_column_to_table(self, user, filter, table):
        contract = []
        match filter:
            case BasicFilters.ALL.value:
                contracts = contract_repo.list_all_contracts()
            case BasicFilters.MINE.value:
                contracts = contract_repo.list_user_contracts(user.id)
            case self.ContractFilters.UNSIGNED.value:
                contracts = contract_repo.list_all_unsigned_contracts()
            case self.ContractFilters.DUE.value:
                contracts = contract_repo.list_all_due_contracts()

        table.add_column("Identifiant", style="cyan")
        table.add_column("Nom du client", style="green")
        table.add_column("Contact du client", style="green")
        table.add_column("Contact commercial chez Epic Events",
                         style="deep_sky_blue3")
        table.add_column("Montant total", style="magenta")
        table.add_column("Restant à payer", style="magenta")
        table.add_column("Date de création", style="pale_violet_red1")
        table.add_column("Dernière mise à jour/contact",
                         style="pale_violet_red1")
        table.add_column("Statut du contrat", style="turquoise2")

        for contract in contracts:
            table.add_row(
                f"{contract.id}",
                contract.client.full_name,
                f"{contract.client.email}\n{contract.client.telephone}",
                contract.user.name,
                f"{contract.amount} €",
                f"{contract.due_amount} €",
                contract.creation_date.strftime("%d/%m/%Y"),
                contract.modified_date.strftime("%d/%m/%Y"),
                contract.status.value,
            )
