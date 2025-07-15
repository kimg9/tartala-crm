from sqlalchemy import URL, create_engine

from models.models import *

from .base import Base

url_object = URL.create("sqlite", database="tartala-crm")

engine = create_engine(url_object, echo=True)

Base.metadata.create_all(engine)
