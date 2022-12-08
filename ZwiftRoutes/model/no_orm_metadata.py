from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Boolean, ForeignKey, text, insert, select

from .base import engine
from .utils.utils import clean_float

worlds = {}

# Simple mapping without ORM
metadata_obj = MetaData()

worlds_table = Table(
    "worlds",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50))
)

routes_table = Table(
    "routes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(200)),
    Column("map", String(50)),
    Column("map_id", Integer, ForeignKey("worlds.id"), nullable=False),
    Column("length", Float),
    Column("elevation", Float),
    Column("lead_in", Float),
    Column("restriction", String(100)),
    Column("badge_xp", Integer),
    Column("completed", Boolean)
)


def insert_worlds_metadata(table_name):
    # execute in same transaction
    with engine.begin() as connection:
        result = connection.execute(text(f"SELECT DISTINCT(Map) FROM {table_name}"))
        # TODO check for empty to avoid duplicates
        # smthing = connection.query(worlds_table).first()
        # if not smthing:
        #     return
        for row in result:
            connection.execute(insert(worlds_table).values(name=row.Map))
            # TODO check documentation form SQL ALCHEMY
            #  first https://docs.sqlalchemy.org/en/14/tutorial/metadata.html then (ALCHEMY ORM) or ORM
            # connection.execute(World.table_name.insert(), {"name": name})


def insert_routes_metadata(table_name):
    with engine.begin() as connection:
        maps_result = connection.execute(select(worlds_table))
        for row in maps_result:
            # store inverted results for later insert of FK
            worlds[row.name] = row.id

    # execute in same transaction
    with engine.begin() as connection:
        result = connection.execute(text(f"SELECT * FROM {table_name}"))

        for row in result:
            connection.execute(insert(routes_table).values(
                [
                    {
                        routes_table.name: row.Name,
                        routes_table.map: row.Map,
                        routes_table.map_id: worlds[row.Map],
                        routes_table.length: clean_float(row.Length),
                        routes_table.elevation: clean_float(row.Elevation),
                        routes_table.lead_in: clean_float(row.LeadIn)
                    }
                ]))
