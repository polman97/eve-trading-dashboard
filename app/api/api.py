
from preston import Preston
from app.api.db.db import save_orders, save_history
from datetime import datetime
import requests

from app.logging_config import get_logger
logging = get_logger()

## initializes preston, the library we use to hit eve esi (it doesnt do much, mainly caching stuff and autoretry for some errors, it might make authing easier)
preston = Preston(
    user_agent='viktor pvolman market dashboard'
)

def get_market_data(item_id, region_id=10000002, location_id=60003760 ) -> list:
    """
    Hits the api for all market orders in a region, then filters out orders that are not in the specified system, and saves the orders to the database
    Args:
        item_id (_type_): TYPID of the item
        region_id (int, optional): Region id . Defaults to 10000002 (the forge).
        location_id (int, optional): Location ID, this doesnt really matter for the api but we parse the results to remove anything outside. Defaults to 60003760 (jita).

    Returns:
        list: a list of dicts with the orders for the item in the system
    """
    logging.info(f'retrieving orders for {item_id}')
    data = preston.get_op('get_markets_region_id_orders', order_type=all, region_id=region_id, type_id=item_id)
    data = [o for o in data if o['location_id'] == location_id ]
    #we change the issued to a format postgresql can read - remember this is in evetime (utc)
    for order in data:
        order['issued'] = datetime.fromisoformat(order['issued'].replace("Z", "+00:00"))
    #saves orders to the db
    save_orders(item_id, data)
    return data
    
def get_region_types(region_id=10000002) -> list:
    """_summary_
    hits api, returns a list of TYPEIDs with orders in the region
    Args:
        region_id (int, optional): region id to get TYPEIDs from. Defaults to 10000002 (the forge).

    Returns:
        list: a list containing all the TYPEIDs with orders in the region
    """
    type_list = []
    i = 1
    #paginated result so we keep hitting the api with page nr += 1
    while True:
        data = preston.get_op('get_markets_region_id_types', region_id=region_id, page=i)
        type_list.extend(data)
        i += 1
        # we dont know how many pages we get, but we do know that a full page is 1000, and the last page (probably) has less then 1k results
        if len (data) < 1000:
            break
    type_list = sorted(type_list)
    return type_list


## WIP
def get_region_history(type_id:int, region_id=10000002) -> list:
    """pulls the region history (last 365 days) of an item.

    Args:
        type_id (int): TYPEID of the item to pull from esi
        region_id (int, optional): region id of history to pull, Defaults to 10000002 (the forge).

    Returns:
        list: _description_
    """
    logging.info(f'retrieving history for {type_id}')
    try:
        data = preston.get_op('get_markets_region_id_history', region_id=region_id, type_id=type_id)
        logging.info(f'attempting to save {len(data)} days of history to the db')    
        save_history(type_id, data)
        return data
    except Exception as e:
        logging.error(Exception)
        return None
    
