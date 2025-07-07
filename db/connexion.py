from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from models import *

from .base import Base


url_object = URL.create("sqlite", database="tartala-crm")

engine = create_engine(url_object, echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
