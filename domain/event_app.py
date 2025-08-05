from datetime import datetime

from db_config.connexion import session
from repositories.events.event_repository import EventRepository

event_repo = EventRepository(session)


class EventApp:
    def get_by_id(self, id):
        return event_repo.get_by_id(id)
    
    def create(self, **kwargs):
        kwargs["creation_date"] = datetime.now()
        kwargs["modified_date"] = datetime.now()

        return event_repo.create_event(**kwargs)

    def update(self, id, **kwargs):
        event = event_repo.get_by_id(id)
        if not event:
            return None

        forbidden_fields = ["id", "creation_date", "modified_date"]

        for key, value in kwargs.items():
            if key not in forbidden_fields:
                if hasattr(event, key):
                    setattr(event, key, value)

        kwargs["modified_date"] = datetime.now()

        event_repo.save_to_db()
        return event

    @staticmethod
    def add_event_column_to_table(table):
        events = event_repo.list_all_events()
        
        table.add_column("Identifiant", style="cyan")
        table.add_column("Identifiant du contrat", style="light_salmon1")
        table.add_column("Nom du client", style="green")
        table.add_column("Contact du client", style="green")
        table.add_column("Date de début", style="magenta")
        table.add_column("Date de fin", style="magenta")
        table.add_column("Contact support chez Epic Events",
                         style="deep_sky_blue3")
        table.add_column("Localisation", style="turquoise2")
        table.add_column("Participants", style="turquoise2")
        table.add_column("Notes", style="pale_violet_red1")

        for event in events:
            table.add_row(
                f"{event.id}",
                f"{event.contract.id}" if event.contract else "",
                event.client.full_name,
                f"{event.client.email}\n{event.client.telephone}",
                event.start.strftime("%d/%m/%Y %H:%M"),
                event.end.strftime("%d/%m/%Y %H:%M"),
                event.user.name,
                event.location,
                f"{event.attendees}",
                event.notes,
            )
