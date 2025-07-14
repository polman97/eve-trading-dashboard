from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from contextlib import contextmanager

from app.db.class_models import Base, MarketOrder, MarketHistory, MarketInsight
from app.logging_config import get_logger

logging = get_logger()

DB_USER = 'gissa'
DB_PASS = 'soetemelk'
DB_HOST = '192.168.178.50' 
DB_PORT = '5432'
DB_NAME = 'eve-market'

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

#TODO understand how sqlalchemy actually works :)

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
# Create tables if they don't exist
Base.metadata.create_all(engine)

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

# Base.metadata.create_all(engine) — optional, run once on init

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        
def count_orders():
    with get_session() as session:
        return session.query(MarketOrder).count()

def count_orders_by_type(type_id: int):
    with get_session() as session:
        return session.query(MarketOrder).filter(MarketOrder.type_id == type_id).count()

def count_history():
    with get_session() as session:
        return session.query(MarketHistory).count()

def count_history_by_type(type_id: int):
    with get_session() as session:
        return session.query(MarketHistory).filter(MarketHistory.type_id == type_id).count()


def save_orders(type_id, orders):
    logging.debug(f'saving {len(orders)} orders for type_id {type_id} to the database')
    with get_session() as session:
        session.query(MarketOrder).filter(MarketOrder.type_id == type_id).delete()

        new_orders = [
            MarketOrder(
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
            ) for o in orders
        ]

        session.bulk_save_objects(new_orders)

def save_history(type_id, history_data):
    logging.debug(f'Saving {len(history_data)} history entries for type_id {type_id} to the database')

    with get_session() as session:
        # Remove existing history for this type_id
        session.query(MarketHistory).filter(MarketHistory.type_id == type_id).delete()

        # Prepare and add new history entries
        new_history = [
            MarketHistory(
                type_id=type_id,
                date=entry['date'],
                average=entry['average'],
                highest=entry['highest'],
                lowest=entry['lowest'],
                order_count=entry['order_count'],
                volume=entry['volume']
            )
            for entry in history_data
        ]

        session.bulk_save_objects(new_history)
        
def save_insight(insight_data: dict):
    logging.debug(f"Saving insights for type_id {insight_data['type_id']} to the database")


    with get_session() as session:
        # Remove any existing insight for this type_id to prevent duplicates
        session.query(MarketInsight).filter(MarketInsight.type_id == insight_data["type_id"]).delete()

        # Create a new MarketInsight instance
        insight = MarketInsight(
            type_id=insight_data["type_id"],
            name=insight_data["name"],
            min_sell=insight_data["min_sell"],
            max_buy=insight_data["max_buy"],
            margin=insight_data["margin"],
            volume=insight_data["volume"],
            volume_7d_avg=insight_data["volume_7d_avg"],
            price_change_1d=insight_data["price_change_1d"],
            price_volatility_7d=insight_data["price_volatility_7d"],
            price_trend_ratio_7d_90d=insight_data["price_trend_ratio_7d_90d"],
            imbalance=insight_data["imbalance"],
            last_updated=insight_data["last_updated"]
        )

        session.add(insight)

def get_orders_df(type_id: int) -> pd.DataFrame:
    with get_session() as session:
        # Query all orders with the given type_id
        orders = session.query(MarketOrder).filter(MarketOrder.type_id == type_id).all()

        # Convert to list of dicts and clean internal state
        orders_dicts = [
            {k: v for k, v in order.__dict__.items() if k != '_sa_instance_state'}
            for order in orders
        ]

        # Create DataFrame
        df = pd.DataFrame(orders_dicts)

    return df

def get_history_df(type_id: int) -> pd.DataFrame:
    with get_session() as session:
        # Query all history entries with the given type_id
        history = session.query(MarketHistory).filter(MarketHistory.type_id == type_id).all()

        # Convert to list of dicts and clean internal state
        history_dicts = [
            {k: v for k, v in entry.__dict__.items() if k != '_sa_instance_state'}
            for entry in history
        ]

        # Create DataFrame
        df = pd.DataFrame(history_dicts)

    return df

def get_insight_type(type_id: int) -> pd.DataFrame:
    with get_session() as session:
        insight = session.query(MarketInsight).filter(MarketInsight.type_id == type_id).first()
        if not insight:
            return pd.DataFrame()  # Empty DF if no data

        insight_dict = {k: v for k, v in insight.__dict__.items() if k != '_sa_instance_state'}
        return pd.DataFrame([insight_dict])
    
def get_insights_full() -> pd.DataFrame:
    with get_session() as session:
        query = session.query(MarketInsight)
        df = pd.read_sql(query.statement, session.bind)
    return df