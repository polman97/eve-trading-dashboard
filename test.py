from app.api.api import get_market_data, get_region_types, get_region_history
from app.api.db.db import get_orders_df, count_orders, count_orders_by_type, get_history_df, get_insight_df
import pandas as pd
from datetime import datetime, timedelta
from preston import Preston
import config_loader

config = config_loader.load_auth_config()

from app.api.math.initial_calcs import basic_inisghts


basic_inisghts(34)
print(get_insight_df(34))