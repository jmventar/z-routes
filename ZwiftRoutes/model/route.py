from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, Float, DateTime
from sqlalchemy.sql import func, expression

from .base import Base


# Route ORM class
class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    name = Column(String(200), unique=True)
    map = Column(String(50))
    map_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    length = Column(Float)
    elevation = Column(Float)
    lead_in = Column(Float)
    restriction = Column(String(100))
    badge_xp = Column(Integer)
    completed = Column(Boolean, server_default=expression.false(), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<id {self.id}, name {self.name}, map {self.map}>"

    # def __init__(self, name, map, map_id, length, elevation, lead_in, restriction, badge_xp, completed):
    #     self.name = name
    #     self.map = map
    #     self.map_id = map_id
    #     self.length = length
    #     self.elevation = elevation
    #     self.lead_in = lead_in
    #     self.restriction = restriction
    #     self.badge_xp = badge_xp
    #     self.completed = completed
