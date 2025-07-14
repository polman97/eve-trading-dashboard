from sqlalchemy import (
    Column, Integer, Float, Boolean, String, DateTime, BigInteger, Date, ForeignKey, UniqueConstraint, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

### These are basically used to setup tables in the postgreSQL database through sqlalchemy. 

class MarketOrder(Base):
    __tablename__ = 'market_orders'
    
    order_id = Column(BigInteger, nullable=False, index=True, unique=True, primary_key=True)  # unique order identifier from API
    type_id = Column(Integer, nullable=False, index=True)  # item ID
    is_buy_order = Column(Boolean, nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume_remain = Column(BigInteger, nullable=False)
    volume_total = Column(BigInteger, nullable=False)
    issued = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    location_id = Column(BigInteger, nullable=False)
    system_id = Column(BigInteger, nullable=True)  # optional if needed
    min_volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    range_ = Column(String, nullable=False)

class MarketHistory(Base):
    __tablename__ = 'market_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, nullable=False, index=True) 
    date = Column(Date, nullable=False, index=True)
    average = Column(Float, nullable=False) 
    highest = Column(Float, nullable=False)                    
    lowest = Column(Float, nullable=False)                    
    order_count = Column(Integer, nullable=False)              
    volume = Column(BigInteger, nullable=False)                   

class MarketInsight(Base):
    __tablename__ = 'market_insights'

    type_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    min_sell = Column(Float, nullable=False)
    max_buy = Column(Float, nullable=False)
    margin = Column(Float, nullable=False)

    volume = Column(Float, nullable=False)
    volume_7d_avg = Column(Float, nullable=False)

    price_change_1d = Column(Float, nullable=False)
    price_volatility_7d = Column(Float, nullable=False)
    price_trend_ratio_7d_90d = Column(Float, nullable=False)

    imbalance = Column(Float, nullable=False)

    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)