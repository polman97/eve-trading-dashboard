import pandas as pd
import time
import os

from app.logging_config import get_logger
from app.api.api import get_market_data

logging = get_logger()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def on_startup():
    logging.info('starting')
    inv_types = invtypes_loader()
    main_loop(inv_types)
    pass


def main_loop(inv_types):
    i = 0
    while True:
        if i >= len(inv_types):
            i = 0
        current_type = inv_types.iloc[i].to_dict()
        current_id = current_type['TYPEID']
        get_market_data(current_id)
        i += 1
        

def invtypes_loader() -> pd.DataFrame:
    """
    Loads the invtypes CSV, parses it by removing anything without a market group (so it only shows tradeable items)
    Returns:
        inv_types: DF containing all the invtypes that are tradeable
    """
    inv_types_path = os.path.join(BASE_DIR, '..', '..', 'SDE', 'invTypes.csv')
    inv_types = pd.read_csv(inv_types_path)
    # clears all invtypes where marketgroupid is nan or an empty str
    inv_types = inv_types[inv_types['MARKETGROUPID'].notna() & (inv_types['MARKETGROUPID'].astype(str).str.strip() != '')]
    return inv_types