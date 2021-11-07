import os
import re
from pathlib import Path
from typing import List, Optional

from config.log import logger
from dotenv import load_dotenv
from requests.sessions import Session

ENV_PATH = Path("./config/") / ".env"
load_dotenv(dotenv_path=ENV_PATH)


STEAM_API_KEY = os.environ["STEAM_API_KEY"]
STEAM_OWNED_GAME_URI = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid=76561197960434622&format=json"
STEAM_OWNED_GAME_LIST = f"https://store.steampowered.com/dynamicstore/userdata/"
STEAM_GAME_LIST = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"


def filter_key(key: str) -> bool:
    pattern = r"([0-9A-Z]{5}-){4}[0-9A-Z]{5}|([0-9A-Z]{5}-){2}[0-9A-Z]{5}"
    return True if re.fullmatch(pattern, key) else False


def is_validated_key(key: str) -> bool:
    # https://steamdb.info
    return filter_key(key)


def get_list_of_owned_games_and_list_of_steam_games(session: Session) -> List[Optional[str]]:
    logger.info("Getting list of owned games.")
    owned_game_list_response = session.get(STEAM_OWNED_GAME_LIST)
    game_list_response = session.get(STEAM_GAME_LIST)

    owned_games_raw_html = owned_game_list_response.content.decode("utf-8")
    game_list_raw_html = game_list_response.content.decode("utf-8")
    owned_games = set(re.findall(r",*([0-9]*),*", owned_games_raw_html))
    steam_games = set(re.findall(r'"appid":([0-9]*)', game_list_raw_html))

    return owned_games, steam_games
