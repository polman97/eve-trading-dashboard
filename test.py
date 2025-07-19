from app.api import get_market_data, get_region_types, get_region_history, get_charater_assets_location
from app.db.db import get_orders_df, count_orders, count_orders_by_type, get_history_df
import pandas as pd
from datetime import datetime, timedelta
from preston import Preston
import config_loader

config = config_loader.load_auth_config()



data = get_charater_assets_location(config['character_id'])
print(data)     

