"""
    in this file we'll do the initial processing as we pull the orders. we basically generate a new entry for the item with:
    TYPEID
    NAME (we can get it from invTypes)
    BUY (highest buy)
    SELL (lowest sell)
    VOLUME (7 day average from history)
    MARGIN (with current skills and standings, might need to figure out first yucky yucky)
    7 day change
    90 day change    
"""
from app.api.db.db import get_orders_df, get_history_df, save_insight, get_insight_df
from app.api.math.utils import get_type_name
import pandas as pd
from datetime import datetime
from app.logging_config import get_logger

logging = get_logger()

def basic_inisghts(type_id):
    try:
        orders_df = get_orders_df(type_id)
        history_df = get_history_df(type_id)
        name = get_type_name(type_id)
        min_sell = orders_df[~orders_df["is_buy_order"]]["price"].min()
        max_buy = orders_df[orders_df["is_buy_order"]]["price"].max()
        margin = calc_margin(max_buy, min_sell)
        last_row = history_df.iloc[-1]
        daily_volume_isk = last_row["volume"] * last_row["average"]
        recent_volume = history_df.sort_values("date").tail(7)["volume"].mean()
        recent_volume_isk = history_df.sort_values("date").tail(7)["average"].mean() * recent_volume 
        daily_change = history_df.sort_values("date").tail(2)["average"].pct_change().iloc[-1]
        price_std_7d = history_df.sort_values("date").tail(7)["average"].std()
        average_7d = history_df.sort_values("date").tail(7)["average"].mean()
        average_90d = history_df.sort_values("date").tail(90)["average"].mean()
        buy_volume = orders_df[orders_df['is_buy_order']]['volume_remain'].sum()
        sell_volume = orders_df[~orders_df['is_buy_order']]['volume_remain'].sum()
        imbalance = (buy_volume - sell_volume) / (buy_volume + sell_volume)
        trend_ratio = average_7d / average_90d if average_90d else None
        insights = {
            "type_id": type_id,
            "name": name,
            "min_sell": float(min_sell),
            "max_buy": float(max_buy),
            "margin" : float(margin),
            "volume": float(daily_volume_isk),
            "volume_7d_avg": float(recent_volume_isk),
            "price_change_1d": float(daily_change),
            "price_volatility_7d": float(price_std_7d),
            "price_trend_ratio_7d_90d": float(trend_ratio),
            "imbalance": float(imbalance),
            "last_updated": datetime.utcnow()
        }

        save_insight(insights)
    
    except Exception as e:
        logging.info(f"could not do calcs for {type_id}")
    
    

def calc_margin(buy_price, sell_price, broker_fee=0.0337, sales_tax=0.0142): 
    buy_fee = buy_price * broker_fee
    sell_fee = sell_price * (broker_fee + sales_tax)
    net_profit = sell_price - sell_fee - buy_price - buy_fee
    return net_profit / buy_price