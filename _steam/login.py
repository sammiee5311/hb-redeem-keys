from config.log import logger
from steam.webauth import WebAuth


def login_steam(username: str, password: str):
    user = WebAuth(username)

    logger.log("Starting login to steam")

    user.cli_login(password)

    return user
