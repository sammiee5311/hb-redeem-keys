import re

from config.log import logger


def filter_key(key):
    logger.info("Filtering the steam key")
    pattern = r"([0-9A-Z]{5}-){4}[0-9A-Z]{5}|([0-9A-Z]{5}-){2}[0-9A-Z]{5}"
    return True if re.fullmatch(pattern, key) else False


def is_validated_key(key):
    # https://steamdb.info
    if filter_key(key):
        pass
