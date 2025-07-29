import sqlalchemy as db

from models.models import Events


class EventRepository:
    def __init__(self, session):
        self.session = session

    def list_all_events(self):
        return self.session.execute(db.select(Events)).scalars().all()

    def create_event(self, **kwargs):
        event = Events(**kwargs)
        self.session.add(event)
        self.session.commit()
        return event
