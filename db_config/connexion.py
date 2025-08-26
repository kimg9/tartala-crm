from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from models.models import *

from .base import Base

url_object = URL.create("sqlite", database="tartala-crm")

engine = create_engine(url_object, echo=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
