
from preston import Preston
from app.db.db import save_orders, save_history
from datetime import datetime
import requests

from app.logging_config import get_logger
logging = get_logger()

## initializes preston, the library we use to hit eve esi (it doesnt do much, mainly caching stuff and autoretry for some errors, it might make authing easier)
import config_loader

config = config_loader.load_auth_config()

preston = Preston(
    user_agent='viktor pvolman market dashboard',
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    callback_url='http://localhost:65432',
    scope=["publicData","esi-calendar.respond_calendar_events.v1","esi-calendar.read_calendar_events.v1","esi-location.read_location.v1","esi-location.read_ship_type.v1","esi-mail.organize_mail.v1","esi-mail.read_mail.v1","esi-mail.send_mail.v1","esi-skills.read_skills.v1","esi-skills.read_skillqueue.v1","esi-wallet.read_character_wallet.v1","esi-wallet.read_corporation_wallet.v1","esi-search.search_structures.v1","esi-clones.read_clones.v1","esi-characters.read_contacts.v1","esi-universe.read_structures.v1","esi-killmails.read_killmails.v1","esi-corporations.read_corporation_membership.v1","esi-assets.read_assets.v1","esi-planets.manage_planets.v1","esi-fleets.read_fleet.v1","esi-fleets.write_fleet.v1","esi-ui.open_window.v1","esi-ui.write_waypoint.v1","esi-characters.write_contacts.v1","esi-fittings.read_fittings.v1","esi-fittings.write_fittings.v1","esi-markets.structure_markets.v1","esi-corporations.read_structures.v1","esi-characters.read_loyalty.v1","esi-characters.read_chat_channels.v1","esi-characters.read_medals.v1","esi-characters.read_standings.v1","esi-characters.read_agents_research.v1","esi-industry.read_character_jobs.v1","esi-markets.read_character_orders.v1","esi-characters.read_blueprints.v1","esi-characters.read_corporation_roles.v1","esi-location.read_online.v1","esi-contracts.read_character_contracts.v1","esi-clones.read_implants.v1","esi-characters.read_fatigue.v1","esi-killmails.read_corporation_killmails.v1","esi-corporations.track_members.v1","esi-wallet.read_corporation_wallets.v1","esi-characters.read_notifications.v1","esi-corporations.read_divisions.v1","esi-corporations.read_contacts.v1","esi-assets.read_corporation_assets.v1","esi-corporations.read_titles.v1","esi-corporations.read_blueprints.v1","esi-contracts.read_corporation_contracts.v1","esi-corporations.read_standings.v1","esi-corporations.read_starbases.v1","esi-industry.read_corporation_jobs.v1","esi-markets.read_corporation_orders.v1","esi-corporations.read_container_logs.v1","esi-industry.read_character_mining.v1","esi-industry.read_corporation_mining.v1","esi-planets.read_customs_offices.v1","esi-corporations.read_facilities.v1","esi-corporations.read_medals.v1","esi-characters.read_titles.v1","esi-alliances.read_contacts.v1","esi-characters.read_fw_stats.v1","esi-corporations.read_fw_stats.v1"],
    refresh_token=config['refresh_token']
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
    logging.debug(f'retrieving orders for {item_id}')
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
def get_region_history(type_id:int, region_id=10000002, save_db=True) -> list:
    """pulls the region history (last 365 days) of an item.

    Args:
        type_id (int): TYPEID of the item to pull from esi
        region_id (int, optional): region id of history to pull, Defaults to 10000002 (the forge).

    Returns:
        list: _description_
    """
    logging.debug(f'retrieving history for {type_id}')
    try:
        data = preston.get_op('get_markets_region_id_history', region_id=region_id, type_id=type_id)
        if save_db:
            logging.debug(f'attempting to save {len(data)} days of history to the db')    
            save_history(type_id, data)
        return data
    except Exception as e:
        logging.error(Exception)
        return None
    

def get_charater_assets_location(character_id:int, location_id=60003760):
    assets = []
    i = 1
    while True:
        data = preston.get_op('get_characters_character_id_assets', character_id = character_id, page=i)
        assets.extend(data)
        i += 1
        if len(data) < 1000:
            break
    assets = [ o for o in assets if o['location_id'] == location_id]
    return assets


