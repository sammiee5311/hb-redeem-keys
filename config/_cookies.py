import pickle

import requests
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from config.log import logger


def load_cookies(file_name: str) -> requests.Session:
    session = requests.Session()
    logger.info(f"Loading cookies from {file_name!r}")
    with open(file_name, "rb") as file:
        cookies = pickle.load(file)
    session.cookies.update(cookies)
    return session


def save_cookies(file_name: str, session: requests.Session):
    with open(file_name, "wb") as file:
        logger.info(f"Saving cookies to {file_name!r}")
        pickle.dump(session.cookies, file)
