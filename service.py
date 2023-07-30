import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

_API_KEY = "KEY_HERE"


class GoogleDriveService:
    def __init__(self):
        self._SCOPES = ["https://www.googleapis.com/auth/drive"]

        _base_path = os.path.dirname(__file__)
        _credential_path = os.path.join(_base_path, "yuli-brand-key.json")
        self._credentials = service_account.Credentials.from_service_account_file(_credential_path, scopes=self._SCOPES)

    def build(self):
        service = build("drive", "v3", credentials=self._credentials, developerKey=_API_KEY)

        return service
