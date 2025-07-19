import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
CSV_PATH = os.path.join(ROOT_DIR, "SDE", "invTypes.csv")

invtypes_df = pd.read_csv(CSV_PATH)
type_map = dict(zip(invtypes_df["TYPEID"], invtypes_df["TYPENAME"]))


def calc_margin(buy_price, sell_price, broker_fee=0.0337, sales_tax=0.0142):
    buy_fee = buy_price * broker_fee
    sell_fee = sell_price * (broker_fee + sales_tax)
    net_profit = sell_price - sell_fee - buy_price - buy_fee
    return net_profit / buy_price


def get_type_name(type_id: int) -> str:
    """Return the type name for a given type ID from the invtypes.csv"""
    result = invtypes_df.loc[invtypes_df["TYPEID"] == type_id, "TYPENAME"]
    return result.values[0] if not result.empty else None



