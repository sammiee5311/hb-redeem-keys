from _steam.login import login_steam
from _steam.validate import validate_key

username = ""
password = ""
key = ""

steam_user = login_steam(username, password)

steam_user.session.get("https://store.steampowered.com/account/registerkey")

response = steam_user.session.post(
    "https://store.steampowered.com/account/ajaxregisterkey/",
    data={"product_key": "6MV5I-TIYNY-4ILMN", "sessionid": steam_user.session_id},
)

if validate_key(key):
    pass
