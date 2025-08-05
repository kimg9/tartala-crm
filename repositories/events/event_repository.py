import sqlalchemy as db

from models.models import Events


class EventRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id):
        pass_query = db.select(Events).where(Events.id == id)
        return self.session.execute(pass_query).scalar_one_or_none()

    def list_all_events(self):
        return self.session.execute(db.select(Events)).scalars().all()

    def create_event(self, **kwargs):
        event = Events(**kwargs)
        self.session.add(event)
        self.session.commit()
        return event

    def save_to_db(self):
        self.session.commit()

    def delete(self, event_id):
        event = self.get_by_id(event_id)
        if event:
            self.session.delete(event)
            self.save_to_db()
            return True
        return False
