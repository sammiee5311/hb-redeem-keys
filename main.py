import requests

from _steam.helper import get_list_of_owned_games, is_validated_key
from _steam.login import login_steam
from config.log import logger
from hb.humblebundle import HumbleBundle

STEAM_REGISTER_KEY = "https://store.steampowered.com/account/registerkey"
STEAM_REGISTER_KEY_URI = "https://store.steampowered.com/account/ajaxregisterkey"

steam_username = ""
steam_password = ""
hb_username = ""
hb_password = ""

steam_user = login_steam(steam_username, steam_password)

steam_user.session.get(STEAM_REGISTER_KEY)

games = get_list_of_owned_games()

hb = HumbleBundle()
hb.login(hb_username, hb_password)
humble_choice_keys = hb.get_humbel_choice_keys()

logger.info("Starting register steam keys.")
for choice_month, choice_keys in humble_choice_keys.items():
    logger.info(f"Filtering {choice_month!r} steam keys")
    for choice_steam_id, choice_key in choice_keys:
        if is_validated_key(choice_key):
            pass
            response = steam_user.session.post(
                STEAM_REGISTER_KEY_URI,
                data={"product_key": choice_key, "sessionid": steam_user.session_id},
            )
