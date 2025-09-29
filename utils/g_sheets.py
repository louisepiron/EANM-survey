from functools import lru_cache
import os
from typing import Tuple, Dict, Any, List

import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Fixed schema to avoid header churn and accelerate writes
HEADERS: List[str] = [
    "timestamp_utc",
    "role",
    "region",
    "familiarity",
    "first_touch",
    "solutions",
    "brand_attributes_ranked",
    "current_problem",
    "channels",
    "formats",
    "video_length",
    "message_choice",
    "likelihood_recommend",
    "improve_one_thing",
    "consent",
    "email",
    "staff_initials",
]

_headers_initialized = False  # module-level guard


def _read_sheet_config():
    # Sheet configuration via secrets or env vars
    try:
        from streamlit import secrets
        sheet_name = secrets["gspread"]["sheet_name"]
        worksheet = secrets["gspread"].get("worksheet", "Responses")
        sa_info = secrets["gcp_service_account"]
    except Exception:
        sheet_name = os.environ.get("GSPREAD_SHEET_NAME")
        worksheet = os.environ.get("GSPREAD_WORKSHEET", "Responses")
        sa_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "")
        if not sheet_name:
            raise RuntimeError(
                "Missing sheet name. Provide st.secrets['gspread']['sheet_name'] or env GSPREAD_SHEET_NAME."
            )
        if not sa_json:
            raise RuntimeError(
                "Missing Google service account credentials. Provide st.secrets['gcp_service_account'] or GCP_SERVICE_ACCOUNT_JSON."
            )
        import json
        sa_info = json.loads(sa_json)

    return sheet_name, worksheet, sa_info


@lru_cache(maxsize=1)
def _get_client() -> gspread.Client:
    sheet_name, worksheet, sa_info = _read_sheet_config()
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPE)
    return gspread.authorize(creds)


@lru_cache(maxsize=8)
def _get_worksheet(sheet_name: str, worksheet: str):
    client = _get_client()
    sh = client.open(sheet_name)
    try:
        ws = sh.worksheet(worksheet)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet, rows=1000, cols=max(50, len(HEADERS)))
    return ws


def _ensure_headers(ws) -> None:
    global _headers_initialized
    if _headers_initialized:
        return
    first_row = ws.row_values(1)
    if not first_row or first_row != HEADERS:
        ws.clear()
        ws.append_row(HEADERS, value_input_option="USER_ENTERED")
    _headers_initialized = True


def append_to_google_sheet(payload: Dict[str, Any]) -> None:
    sheet_name, worksheet, _ = _read_sheet_config()
    ws = _get_worksheet(sheet_name, worksheet)
    _ensure_headers(ws)

    # Build row in fixed order; flatten lists to comma-separated strings.
    row = []
    for key in HEADERS:
        val = payload.get(key, "")
        if isinstance(val, list):
            val = ", ".join(val)
        row.append(val)
    ws.append_row(row, value_input_option="USER_ENTERED")


def healthcheck_google_sheet() -> Tuple[bool, str]:
    try:
        sheet_name, worksheet, _ = _read_sheet_config()
        ws = _get_worksheet(sheet_name, worksheet)
        _ = ws.title
        return True, "ok"
    except Exception as e:
        return False, str(e)
