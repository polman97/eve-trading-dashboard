from app.api.api import get_market_data, get_region_types, get_region_history
from app.api.db.db import get_orders_df, count_orders, count_orders_by_type, get_history_df
import pandas as pd
from datetime import datetime, timedelta
df = get_history_df(31704)


df = get_history_df(31704)
df['date'] = pd.to_datetime(df['date'])
latest_date_db = df['date'].max().date()
api_plex = pd.DataFrame(get_region_history(31704, save_db=False))
api_plex['date'] = pd.to_datetime(api_plex['date'])
latest_date_api = api_plex['date'].max().date()
if latest_date_db == latest_date_api: