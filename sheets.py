import os
import json
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
from dotenv import load_dotenv
import io

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class GoogleSheetsClient:

    def __init__(self):
        creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        creds_full_path = os.path.join(base_dir, creds_path)

        self.creds = Credentials.from_service_account_file(
            creds_full_path,
            scopes=SCOPES
        )

        self.client = gspread.authorize(self.creds)
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
        self.sheet = self.client.open_by_key(self.sheet_id).worksheet("Notes de frais")
        self.drive_service = build("drive", "v3", credentials=self.creds)
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

    def upload_image_to_drive(self, image_bytes: bytes, filename: str, media_type: str) -> str:
        file_metadata = {
            "name": filename,
            "parents": [self.folder_id]
        }

        media = MediaIoBaseUpload(
            io.BytesIO(image_bytes),
            mimetype=media_type,
            resumable=True
        )

        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file.get("id")

        self.drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()

        return f"https://drive.google.com/uc?id={file_id}"

    def append_expense(self, data: dict, image_url: str = None) -> None:
        row = [
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            data.get("type_document", None),
            data.get("fournisseur", None),
            data.get("date", None),
            data.get("montant_ttc", None),
            data.get("tva", None),
            data.get("devise", "EUR"),
            data.get("description", None),
            data.get("confiance", None),
            f'=IMAGE("{image_url}")' if image_url else None
        ]

        self.sheet.append_row(row, value_input_option="USER_ENTERED")