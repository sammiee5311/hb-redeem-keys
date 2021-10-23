import json

import requests
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from config.log import logger


def load_cookies(file_name: str) -> requests.Session:
    session = requests.Session()
    logger.info("Loading cookies from {file_name!r}")
    cookies = cookiejar_from_dict(json.load(file_name))
    session.cookies.update(cookies)

    return session


def save_cookies(file_name: str, session: requests.Session):
    with open(file_name, "wb") as file:
        logger.info("Saving cookies to {file_name!r}")
        cookies = dict_from_cookiejar(session.cookies)
        json.dump(cookies, file)
