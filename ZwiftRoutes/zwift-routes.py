from datetime import date

from bs4 import BeautifulSoup
from pandas import DataFrame
from requests import get
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import database_exists, create_database

from model.base import engine, Base, session_factory
from model.route import Route
from model.utils.utils import clean_float
from model.world import World

SOURCES = "./route_sources.txt"


# Store given dataframe into DB
def store_dataframe(df, table_name):
    # Open DB connection
    with engine.connect() as con:
        try:
            df.to_sql(table_name, con, if_exists='replace')

        except ValueError as vx:
            print(vx)

        except Exception as ex:
            print(ex)

        else:
            print("Table %s created successfully." % table_name)

        finally:
            con.close()


def prepare_orm_database():
    # Create DB if not exists
    if not database_exists(engine.url):
        create_database(engine.url)
        Base.metadata.create_all(engine)


def insert_worlds(table_name):
    # retrieve a session
    session = session_factory()

    # if session.query(World).first():
    #     print("there are already some worlds, skip...")
    #     return

    # execute in same transaction
    result = session.execute(text(f"SELECT DISTINCT(Map) FROM {table_name}"))
    for row in result:
        q = session.query(World)
        q = q.filter(World.name == row.Map)
        try:
            q.one()
        except SQLAlchemyError as e:
            session.add(World(name=row.Map))

    session.commit()
    print(f"DB contains {result.rowcount} worlds")


def insert_routes(table_name):
    session = session_factory()

    db_worlds = session.query(World).all()

    raw_count = session.execute(text(f"SELECT COUNT(1) FROM {table_name}")).scalar()
    routes_count = session.query(Route).count()
    update_count: int = 0
    insert_count: int = 0

    print(f"Found {raw_count} entries in {table_name}, current existing Routes in DB: {routes_count}")

    # find raw data and insert into routes
    result = session.execute(text(f"SELECT * FROM {table_name}"))
    for row in result:
        q = session.query(Route)
        q = q.filter(Route.name == row.route)
        try:
            record = q.one_or_none()
            if record:
                # TODO Try to avoid update if record fields are the same
                record.name = row.route
                record.map = row.map
                record.map_id = [x.id for x in db_worlds if x.name == row.map]
                record.length = clean_float(row.length)
                record.elevation = clean_float(row.elevation)
                record.lead_in = clean_float(row.lead_in)
                record.restriction = row.restriction
                update_count += 1
            else:
                session.add(Route(
                    name=row.route,
                    map=row.map,
                    map_id=[x.id for x in db_worlds if x.name == row.map],
                    length=clean_float(row.length),
                    elevation=clean_float(row.elevation),
                    lead_in=clean_float(row.lead_in),
                    restriction=row.restriction
                ))
                insert_count += 1
        except SQLAlchemyError as e:
            print(e)

        session.commit()

    print(f"From {raw_count} entries in {table_name}, inserted: {insert_count}, updated: {update_count} routes in "
          f"DB {routes_count}")


def main():
    links = []

    with open(SOURCES) as file:
        for line in file:
            links.append(line)

    # Currently only use first one
    page = get(links[0])

    if not page.ok:
        print("Page not found")
        return

    soup = BeautifulSoup(page.text, 'html.parser')
    table_data = soup.find('table')

    headers = []

    # Retrieve all table headers
    for i in table_data.find_all('th'):
        title = i.text.strip().replace("-","_").lower()
        headers.append(title)

    df = DataFrame(columns=headers)

    # Retrieve all table values
    for j in table_data.find_all('tr')[1:]:
        row_data = j.find_all('td')
        row = [tr.text for tr in row_data]
        length = len(df)
        df.loc[length] = row

    raw_table = f"raw_{date.today().strftime('%Y%m%d')}"

    # Prepare database
    prepare_orm_database()

    # store raw
    store_dataframe(df, raw_table)

    # Working with DB NO ORM
    # prepare_metadata()
    # insert_worlds_metadata(raw_table)
    # insert_routes_metadata(raw_table)

    insert_worlds(raw_table)
    insert_routes(raw_table)


if __name__ == '__main__':
    main()
