import streamlit as st
import pandas as pd
import json
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Product Gallery",
    page_icon="🛍️",
    layout="wide"
)

# --------------------------------------------------
# Utilities
# --------------------------------------------------
REQUIRED_SERVICE_KEYS = {
    "type",
    "project_id",
    "private_key",
    "client_email",
    "token_uri"
}

def validate_private_key(key: str) -> bool:
    return (
        "BEGIN PRIVATE KEY" in key
        and "END PRIVATE KEY" in key
        and "\n" in key
    )

# --------------------------------------------------
# Google Sheets Client (HARD VALIDATION)
# --------------------------------------------------
@st.cache_resource
def get_google_sheets_client():
    try:
        # 1️⃣ Secrets existence
        if "gcp_service_account_json" not in st.secrets:
            st.error("❌ Missing secret: gcp_service_account_json")
            st.stop()

        raw_json = st.secrets["gcp_service_account_json"]

        # 2️⃣ JSON parsing
        try:
            creds_dict = json.loads(raw_json)
        except json.JSONDecodeError as e:
            st.error("❌ Service account JSON is INVALID")
            st.code(str(e))
            st.stop()

        # 3️⃣ Required keys check
        missing = REQUIRED_SERVICE_KEYS - creds_dict.keys()
        if missing:
            st.error("❌ Service account JSON is missing required fields")
            st.code(", ".join(missing))
            st.stop()

        # 4️⃣ Private key sanity check
        if not validate_private_key(creds_dict["private_key"]):
            st.error("❌ Private key format is INVALID")
            st.info("Key must include BEGIN/END PRIVATE KEY and \\n line breaks")
            st.stop()

        # 5️⃣ Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly"
            ]
        )

        # 6️⃣ Build service
        return build("sheets", "v4", credentials=credentials)

    except Exception as e:
        st.error("❌ Fatal error while initializing Google Sheets client")
        st.exception(e)
        st.stop()

# --------------------------------------------------
# Load Sheet Data
# --------------------------------------------------
@st.cache_data(ttl=300)
def load_sheet(sheet_id: str, sheet_name: str):
    try:
        service = get_google_sheets_client()

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=sheet_name
        ).execute()

        values = result.get("values", [])

        if not values:
            st.warning("⚠ Sheet exists but contains NO DATA")
            return None

        headers = values[0]
        rows = values[1:]

        if not headers:
            st.error("❌ Sheet header row is empty")
            return None

        return pd.DataFrame(rows, columns=headers)

    except HttpError as e:
        if e.resp.status == 404:
            st.error("❌ Sheet ID not found or not shared with service account")
        elif e.resp.status == 403:
            st.error("❌ Permission denied. Share the sheet with the service account email.")
        else:
            st.error("❌ Google API error")
            st.exception(e)
        return None

    except Exception as e:
        st.error("❌ Unexpected error while loading sheet")
        st.exception(e)
        return None

# --------------------------------------------------
# Media Helpers
# --------------------------------------------------
def is_video(url: str) -> bool:
    return bool(re.search(r"\.(mp4|webm|mov|avi|mkv)$", url, re.I))

def render_media(url: str):
    try:
        if is_video(url):
