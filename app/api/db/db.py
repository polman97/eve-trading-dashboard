from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from app.api.db.class_models import Base, MarketOrder, MarketHistory
from app.logging_config import get_logger

logging = get_logger()

DB_USER = 'gissa'
DB_PASS = 'soetemelk'
DB_HOST = '192.168.178.50' 
DB_PORT = '5432'
DB_NAME = 'eve-market'

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

#TODO understand how sqlalchemy actually works :)

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
# Create tables if they don't exist
Base.metadata.create_all(engine)

def count_orders():
    return session.query(MarketOrder).count()

def count_orders_by_type(type_id):
    return session.query(MarketOrder).filter(MarketOrder.type_id == type_id).count()

def count_history():
    return session.query(MarketHistory).count()

def count_history_by_type(type_id):
    return session.query(MarketHistory).filter(MarketHistory.type_id == type_id).count()


def reset_market_orders_table():
    # Drop only the market_orders table
    Base.metadata.drop_all(engine, tables=[Base.metadata.tables['market_orders']])
    # Recreate the market_orders table with the current schema
    Base.metadata.create_all(engine, tables=[Base.metadata.tables['market_orders']])
    print("market_orders table has been reset.")

def save_orders(type_id, orders):
    logging.info(f'saving {len(orders)} orders for type_id {type_id} to the database')
    # Remove existing orders for this type_id
    session.query(MarketOrder).filter(MarketOrder.type_id == type_id).delete()
    # Prepare and add new orders
    new_orders = []
    for o in orders:
        order = MarketOrder(
            order_id=o['order_id'],
            type_id=o['type_id'],
            system_id=o['system_id'],
            location_id=o['location_id'],
            is_buy_order=o['is_buy_order'],
            price=o['price'],
            volume_total=o['volume_total'],
            volume_remain=o['volume_remain'],
            min_volume=o['min_volume'],
            duration=o['duration'],
            range_=o['range'],
            issued=o['issued']
        )
        new_orders.append(order)

    session.bulk_save_objects(new_orders)
    session.commit()

def save_history(type_id, history_data):
    logging.info(f'Saving {len(history_data)} history entries for type_id {type_id} to the database')

    # Remove existing history for this type_id
    session.query(MarketHistory).filter(MarketHistory.type_id == type_id).delete()

    # Prepare and add new history entries
    new_history = []
    for h in history_data:
        entry = MarketHistory(
            type_id=type_id,
            date=h['date'],
            average=h['average'],
            highest=h['highest'],
            lowest=h['lowest'],
            order_count=h['order_count'],
            volume=h['volume']
        )
        new_history.append(entry)

    session.bulk_save_objects(new_history)
    session.commit()

def get_orders_df(type_id: int) -> pd.DataFrame:
    with Session() as session:
        # Query all orders with the given type_id
        orders = session.query(MarketOrder).filter(MarketOrder.type_id == type_id).all()

        # Convert to list of dicts
        orders_dicts = [order.__dict__ for order in orders]

        # Remove SQLAlchemy internal state key
        for d in orders_dicts:
            d.pop('_sa_instance_state', None)

        # Create DataFrame
        df = pd.DataFrame(orders_dicts)
    return df

def get_history_df(type_id: int) -> pd.DataFrame:
    with Session() as session:
        # Query all history entries with the given type_id
        history = session.query(MarketHistory).filter(MarketHistory.type_id == type_id).all()

        # Convert to list of dicts
        history_dicts = [entry.__dict__ for entry in history]

        # Remove SQLAlchemy internal state key
        for d in history_dicts:
            d.pop('_sa_instance_state', None)

        # Create DataFrame
        df = pd.DataFrame(history_dicts)
    return df