from __future__ import print_function

import base64
import os.path
import platform
import re
from typing import Any, Union

import backoff
from bs4 import BeautifulSoup
from config.log import logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_PATH = "config/gmail/credentials.json"
TOKEN_PATH = "config/gmail/token.json"


class NotFoundEmail(Exception):
    pass


def trying_to_find(e):
    print("Humble Bundle Email Protection is not yet found.")


class GmailAPI:
    messages: dict[str, str]  # id, threadId
    services: Resource
    creds: Credentials = None

    def save_token(self):
        logger.info("Saving token for gmail authentication.")
        with open(TOKEN_PATH, "w") as token:
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
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                self.creds = flow.run_local_server(port=0)

            self.save_token()

    def get_gmail_service(self):
        return build("gmail", "v1", credentials=self.creds)

    def get_latest_emails(self):
        self.service = self.get_gmail_service()

        results = self.service.users().messages().list(userId="me").execute()
        self.messages = results.get("messages")

    def process_gmail_api(self) -> None:
        if os.path.exists(TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        self.check_and_save_token_if_creds_not_valid()

        self.get_latest_emails()

    def decode_email(self, payload: dict[str, Union[str, list[dict[str, Any]]]]) -> str:
        logger.info("Decoding email content from gmail.")

        parts = payload.get("parts")[0]
        data = parts["body"]["data"]
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)

        if platform.system().lower() == "windows":
            soup = BeautifulSoup(decoded_data, "lxml")
            body = soup.body()

            return str(body[0])
        else:
            decoded_data = decoded_data.decode("utf8")

            return decoded_data

    def is_humble_bundle_email(self, headers) -> bool:
        for d in headers:
            if d["name"] == "From" and "Humble Bundle" in d["value"]:
                logger.info("Getting humble bundle account protection.")
                return True

        return False

    @backoff.on_exception(backoff.expo, NotFoundEmail, max_tries=10, giveup=trying_to_find)
    def get_humble_bundle_account_protection(self) -> str:
        self.get_latest_emails()

        for i, msg in enumerate(self.messages):
            if i > 2:
                raise NotFoundEmail("Could not Find humble bundle account protection.")
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
