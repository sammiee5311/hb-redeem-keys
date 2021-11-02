import requests

from _steam.helper import get_list_of_owned_games, is_validated_key
from _steam.login import login_steam
from config.log import logger
from hb.humblebundle import HumbleBundle

STEAM_REGISTER_KEY = "https://store.steampowered.com/account/registerkey"
STEAM_REGISTER_KEY_URI = "https://store.steampowered.com/account/ajaxregisterkey"

username = ""
password = ""

steam_user = login_steam(username, password)

steam_user.session.get(STEAM_REGISTER_KEY)

games = get_list_of_owned_games()


hb = HumbleBundle()
hb.login()

key = ""

if is_validated_key(key):
    logger.info("Starting register steam keys.")
    response = steam_user.session.post(
        STEAM_REGISTER_KEY_URI,
        data={"product_key": key, "sessionid": steam_user.session_id},
    )
