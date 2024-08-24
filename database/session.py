from sqlalchemy.orm import sessionmaker
from .database import engine

session = sessionmaker(engine)
