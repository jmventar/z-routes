from sqlalchemy import Column, String, Integer

from .base import Base


# World ORM class
class World(Base):
    __tablename__ = "worlds"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    name = Column(String(50), unique=True)

    def __repr__(self):
        return f"<name {self.name}>"
    # def __init__(self, name):
    #     self.name = name



