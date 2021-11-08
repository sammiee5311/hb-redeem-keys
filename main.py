from time import sleep

from _steam.helper import (
    get_list_of_owned_games_and_list_of_steam_games,
    is_validated_key,
)
from _steam.login import login_steam
from config.log import logger
from hb.humblebundle import HumbleBundle

STEAM_REGISTER_KEY = "https://store.steampowered.com/account/registerkey"
STEAM_REGISTER_KEY_URI = "https://store.steampowered.com/account/ajaxregisterkey"
_time = 1


def wait_for_next_key_redeem():
    global _time
    sleep(_time * 2)
    _time += 1


steam_username = ""
steam_password = ""
hb_username = ""
hb_password = ""

steam_user = login_steam(steam_username, steam_password)

steam_user.session.get(STEAM_REGISTER_KEY)

owned_games, steam_games = get_list_of_owned_games_and_list_of_steam_games(steam_user.session)

hb = HumbleBundle()
hb.login(hb_username, hb_password, gmail_access=True)
humble_choice_keys = hb.get_humbel_choice_keys()

logger.info("Starting register steam keys.")

for choice_month, choice_keys in humble_choice_keys.items():
    logger.info(f"Filtering {choice_month!r} steam keys")
    for choice_steam_id, choice_key in choice_keys:
        if is_validated_key(choice_key) and choice_steam_id not in owned_games and choice_steam_id in steam_games:
            response = steam_user.session.post(
                STEAM_REGISTER_KEY_URI,
                data={"product_key": choice_key, "sessionid": steam_user.session_id},
            )
            owned_games.add(choice_steam_id)
            wait_for_next_key_redeem()
