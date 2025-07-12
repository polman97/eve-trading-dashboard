from app.api.api import get_market_data
from app.api.db.db import get_orders_df, reset_market_orders_table, count_orders, count_orders_by_type

print(count_orders())

data = get_market_data(34)
buys = [o for o in data if o['is_buy_order']]
sells = [o for o in data if not o['is_buy_order']]

print(count_orders_by_type(34))
print(get_orders_df(34))
# Max buy price
max_buy = max(buys, key=lambda o: o['price'])['price'] if buys else None
min_sell = min(sells, key=lambda o: o['price'])['price'] if sells else None

