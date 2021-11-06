from __future__ import print_function

import base64
import os.path
import re
from typing import Any, Union

import backoff
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from config.log import logger

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class NotFoundEmail(Exception):
    pass


def trying_to_find(e):
    print("Humble Bundle Email Protection is not yet found.")


class GmailAPI:
    messages: dict[str, str]  # id, threadId
    services: Resource
    creds: Credentials = None
    TOKEN_PATH: str
    CREDENTIALS_PATH: str

    def __init__(self, token_path: str = "token.json", credentials_path: str = "credentials.json"):
        self.TOKEN_PATH = token_path
        self.CREDENTIALS_PATH = credentials_path

    def save_token(self):
        logger.info("Saving token for gmail authentication.")
        with open(self.TOKEN_PATH, "w") as token:
            token.write(self.creds.to_json())

    def is_not_valid_creds(self) -> bool:
        return not self.creds or not self.creds.valid

    def has_expired_creds(self) -> bool:
        return self.creds and self.creds.expired and self.creds.refresh_token

    def check_and_save_token_if_creds_not_valid(self):
        if self.is_not_valid_creds():
            if self.has_expired_creds():
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_PATH, SCOPES)
                self.creds = flow.run_local_server(port=0)

            self.save_token()

    def set_messages_from_gmail(self) -> None:
        logger.info("Getting emails content from gmail.")

        if os.path.exists(self.TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(self.TOKEN_PATH, SCOPES)

        self.check_and_save_token_if_creds_not_valid()

        self.service = build("gmail", "v1", credentials=self.creds)

        results = self.service.users().messages().list(userId="me").execute()
        self.messages = results.get("messages")

    def decode_email(self, payload: dict[str, Union[str, list[dict[str, Any]]]]) -> str:
        logger.info("Decoding email content from gmail.")

        parts = payload.get("parts")[0]
        data = parts["body"]["data"]
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)
        soup = BeautifulSoup(decoded_data, "lxml")
        body = soup.body()

        return str(body[0])

    def is_humble_bundle_email(self, headers) -> bool:
        for d in headers:
            if d["name"] == "From" and "Humble Bundle" in d["value"]:
                logger.info("Getting humble bundle account protection.")
                return True

        return False

    @backoff.on_exception(backoff.expo, NotFoundEmail, max_tries=5, giveup=trying_to_find)
    def get_humble_bundle_account_protection(self) -> str:
        for i, msg in enumerate(self.messages):
            if i > 2:
                raise NotFoundEmail("Could not Found humble bundle account protection.")
            txt = self.service.users().messages().get(userId="me", id=msg["id"]).execute()

            try:
                payload = txt["payload"]
                headers = payload["headers"]

                if self.is_humble_bundle_email(headers):
                    email_content = self.decode_email(payload)
                    code = re.search(r"[A-Z0-9]{7}", email_content).group(0)

                    return code

            except:
                pass
