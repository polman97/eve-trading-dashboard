from app.api.api import get_market_data, get_region_types
from app.api.db.db import get_orders_df, reset_market_orders_table, count_orders, count_orders_by_type

print(count_orders())

