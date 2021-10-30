import os

from config._cookies import load_cookies, save_cookies
from config.log import logger
from steam.webauth import WebAuth

STEAM_COOKIES = "config/steam_cookie.pkl"


def login_steam(username: str, password: str = "") -> WebAuth:
    user = WebAuth(username)
    logger.info("Starting login to steam")

    if os.path.exists(STEAM_COOKIES):
        session = load_cookies(STEAM_COOKIES)
        user.session = session
        user.session_id = user.session.cookies.get_dict()["sessionid"]
        user.logged_on = True
    else:
        session = user.cli_login(password)
        save_cookies(STEAM_COOKIES, session)

    return user
