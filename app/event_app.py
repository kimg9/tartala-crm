from datetime import datetime

from db_config.connexion import session
from repositories.events.event_repository import EventRepository

event_repo = EventRepository(session)


class EventApp:
    def create(self, **kwargs):
        kwargs["creation_date"] = datetime.now()
        kwargs["modified_date"] = datetime.now()

        return event_repo.create_event(**kwargs)
