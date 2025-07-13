import pandas as pd
import time
import os
import sys
from datetime import datetime, timedelta

from app.logging_config import get_logger
from app.api.api import get_market_data, get_region_types, get_region_history
from app.api.db.db import get_history_df

logging = get_logger()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def on_startup():
    logging.info('starting')
    main_loop()
    pass


def main_loop():
    #returns a list of item_id's 
    region_types = get_region_types()
    # we pull market history in our db for plex. if the latest entry is older then yesterday, then we have to update it
    df = get_history_df(31704)
    df['date'] = pd.to_datetime(df['date'])
    latest_date_db = df['date'].max().date()
    api_plex = pd.DataFrame(get_region_history(31704, save_db=False))
    api_plex['date'] = pd.to_datetime(api_plex['date'])
    latest_date_api = api_plex['date'].max().date()
    if latest_date_db == latest_date_api:
        logging.info(f"Latest data is up to date, last history pull: {latest_date_api}")
    else:
        logging.info(f'history is out of date, latest history pull: {latest_date_api}. retriving market history for {len(region_types)} TYPEIDs')
        i = 1
        for current_id in region_types:
            get_region_history(current_id)
            i += 1
            if i % 100 == 0:
                logging.info(f'Retrieved market history for {i}/{len(region_types)} TYPEIDs')
        logging.info('Finished retrieving market history.')
    #pulls all orders for each item_id and then updates the db 
    i = 1
    logging.info(f'Retrieving market orders for {len(region_types)} TYPEIDs')
    for current_id in region_types:
        get_market_data(current_id)
        i += 1
        if i % 100 == 0:
            logging.info(f'Retrieved market orders for {i}/{len(region_types)} TYPEIDs')
    #exits the app, at wich point docker will automatically restart #FIXME this is a bandaid, gotta figure out what's leaking memory
    logging.info('Finished retrieving and processing orders for all items, restarting cause lmao memory leak')
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

