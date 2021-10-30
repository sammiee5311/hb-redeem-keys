import os
import re
from pathlib import Path

import requests
from config.log import logger
from dotenv import load_dotenv

ENV_PATH = Path("./config/") / ".env"
load_dotenv(dotenv_path=ENV_PATH)


STEAM_API_KEY = os.environ["STEAM_API_KEY"]


def filter_key(key):
    logger.info("Filtering the steam key")
    pattern = r"([0-9A-Z]{5}-){4}[0-9A-Z]{5}|([0-9A-Z]{5}-){2}[0-9A-Z]{5}"
    return True if re.fullmatch(pattern, key) else False


def is_validated_key(key):
    # https://steamdb.info
    return filter_key(key)


def get_list_of_owned_games():
    logger.info("Getting list of owned games.")
    response = requests.get(
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid=76561197960434622&format=json"
    )

    raw_html = response.content.decode("utf-8")
    games = re.findall(r'"appid":([0-9]*)', raw_html)

    return games