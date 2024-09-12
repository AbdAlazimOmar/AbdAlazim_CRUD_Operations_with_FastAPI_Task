from sqlalchemy import (Column, Float, Integer, MetaData, String, Table,create_engine)
from sqlalchemy.engine import Engine

DATABASE_URL: str = "sqlite:///./car_task.db"

engine: Engine = create_engine(DATABASE_URL)

metadata: MetaData = MetaData()

cars_table = Table(
    'cars', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
    Column('model', String, nullable=False),
    Column('year', Integer, nullable=False),
    Column('price', Float, nullable=False)
)

