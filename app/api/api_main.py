import pandas as pd
import time
import os
import sys

from app.logging_config import get_logger
from app.api.api import get_market_data, get_region_types, get_region_history

logging = get_logger()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def on_startup():
    logging.info('starting')
    main_loop()
    pass


def main_loop():
    #returns a list of item_id's 
    region_types = get_region_types()
    #pulls history for region and updates db
    for current_id in region_types:
        get_region_history(current_id)
    #pulls all orders for each item_id and then updates the db 
    for current_id in region_types:
        get_market_data(current_id)
    #exits the app, at wich point docker will automatically restart #FIXME this is a bandaid, gotta figure out what's leaking memory
    time.sleep(10)
    sys.exit(0)

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

