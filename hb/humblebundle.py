import os
import platform
import re
from collections import OrderedDict, defaultdict
from time import sleep
from typing import Optional

import backoff
import pydantic
import requests
import selenium.webdriver
from config._cookies import load_cookies, save_cookies
from pydantic import constr
from pydantic.dataclasses import dataclass
from selenium.webdriver.common.by import By

CHROME_DRIVER = "hb/chromedriver.exe" if platform.system().lower() == "windows" else "hb/chromedriver"

HB_ORDER_HISTORIES_URI = "https://www.humblebundle.com/api/v1/user/order"
HB_ORDER_EACH_HISTORY_URI = "https://www.humblebundle.com/api/v1/order"
HB_LOGIN_URI = "https://www.humblebundle.com/login"
HB_LOGIN_PROCESS_URI = "https://www.humblebundle.com/processlogin"
HB_COOKIES = "config/hb_cookies.pkl"
HB_HEADERS = OrderedDict(
    {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "csrf-prevention-token": "",
        "x-requested-with": "XMLHttpRequest",
    }
)


@dataclass
class HumbleBundleParameters:
    access_token: Optional[str] = ""
    access_token_provider_id: Optional[str] = ""
    goto: str = "/"
    password: Optional[str] = ""
    qs: Optional[str] = ""
    username: Optional[str] = ""


@dataclass
class Account:
    username: constr(min_length=2)
    password: constr(min_length=2)


def too_many_tried(e):
    print("Too many tried logged in.")


class HumbleBundle:
    account: Account
    session: requests.Session
    logged_on: bool
    driver_path: str
    __choice_keys: defaultdict[str, list[tuple]] = defaultdict(list)

    @staticmethod
    @backoff.on_exception(backoff.expo, pydantic.error_wrappers.ValidationError, max_tries=3, giveup=too_many_tried)
    def get_account():
        username = input("Please, type humble bundle email: ")
        password = input("Please, type humble bundle password: ")
        account = Account(username, password)
        return account

    def set_humble_choice_keys(self, response):
        for data in response.json():
            gamekey_json = data["gamekey"]
            each_response = self.session.get(
                f"{HB_ORDER_EACH_HISTORY_URI}/{gamekey_json}?all_tpkds=true"
            ).content.decode("utf8")
            month = re.findall(r'"choice_url":"([a-z]*)', each_response)
            if month:
                self.__choice_keys[month[0]] = zip(
                    re.findall(r'"steam_app_id":([0-9]*)', each_response),
                    re.findall(r'"redeemed_key_val":"([0-9A-Z]{5}-[0-9A-Z]{5}-[0-9A-Z]{5})', each_response),
                )

    def login_with_seleninum(self, session: requests.Session):

        driver = selenium.webdriver.Chrome()
        driver.get("https://www.humblebundle.com/login")
        driver.find_element(by=By.NAME, value="username").send_keys(self.account.username)
        driver.find_element(by=By.NAME, value="password").send_keys(self.account.password)
        driver.find_element(
            by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div/div/section[1]/form/button"
        ).click()
        sleep(40)
        for cookie in driver.get_cookies():
            session.cookies[cookie["name"]] = cookie["value"]
        save_cookies(HB_COOKIES, session)

        return session

    def login(self, username: str = "", password: str = ""):
        if not username or not password:
            self.account = self.get_account()
        else:
            self.account = Account(username, password)

        session = requests.Session()

        if os.path.exists(HB_COOKIES):
            self.session = load_cookies(HB_COOKIES)
        else:
            self.session = self.login_with_seleninum(session)

    def get_humbel_choice_keys(self):
        response = self.session.get(HB_ORDER_HISTORIES_URI)

        self.set_humble_choice_keys(response)

        return self.__choice_keys
