# models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from database.connection import engine  # assumes you have database/connection.py

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    role = Column(String(50))

# Create tables if they don't exist
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()