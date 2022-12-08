import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load ENV vars
load_dotenv()

DB_IP = os.getenv("ZR_DATABASE_DOCKER_IP")
DB_NAME = os.getenv("ZR_DATABASE_NAME")
DB_USER = os.getenv("ZR_DATABASE_USER")
DB_PASSWORD = os.getenv("ZR_DATABASE_PASSWORD")

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_IP}/{DB_NAME}")

# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
