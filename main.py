from _steam.login import login_steam
from _steam.validate import is_validated_key

STEAM_REGISTER_KEY = "https://store.steampowered.com/account/registerkey"
STEAM_REGISTER_KEY_URI = "https://store.steampowered.com/account/ajaxregisterkey"

username = ""
password = ""

steam_user = login_steam(username, password)

steam_user.session.get(STEAM_REGISTER_KEY)

response = steam_user.session.post(
    STEAM_REGISTER_KEY_URI,
    data={"product_key": "", "sessionid": steam_user.session_id},
)

if is_validated_key(key=""):
    pass
