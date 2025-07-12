
from preston import Preston
from app.api.db.db import save_orders
from datetime import datetime

from app.logging_config import get_logger
logging = get_logger()

preston = Preston(
    user_agent='viktor pvolman market dashboard'
)

def get_market_data(item_id, region_id=10000002, location_id=60003760 ):
    logging.info(f'retrieving orders for {item_id}')
    data = preston.get_op('get_markets_region_id_orders', order_type=all, region_id=region_id, type_id=item_id)
    data = [o for o in data if o['location_id'] == location_id ]
    for order in data:
        order['issued'] = datetime.fromisoformat(order['issued'].replace("Z", "+00:00"))
    save_orders(item_id, data)
    return data
    
def get_region_types(region_id=10000002):
    type_list = []
    i = 1
    while True:
        data = preston.get_op('get_markets_region_id_types', region_id=region_id, page=i)
        type_list.extend(data)
        i += 1
        if len (data) < 1000:
            break
    type_list = sorted(type_list)
    return type_list

def get_region_history(region_id, item_id):
    data = preston.get_op('get_markets_region_id_history', region_id=region_id, type_id=item_id)
