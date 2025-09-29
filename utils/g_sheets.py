import os
from typing import Tuple, Dict, Any

import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def _get_client() -> gspread.Client:
    # Expect service account json in Streamlit secrets
    try:
        from streamlit import secrets
        sa_info = secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(sa_info, scopes=SCOPE)
    except Exception:
        # Fallback to env var GCP_SERVICE_ACCOUNT_JSON (stringified JSON)
        import json
        sa_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "")
        if not sa_json:
            raise RuntimeError(
                "Missing Google service account credentials. Provide st.secrets['gcp_service_account'] or GCP_SERVICE_ACCOUNT_JSON."
            )
        creds = Credentials.from_service_account_info(json.loads(sa_json), scopes=SCOPE)

    return gspread.authorize(creds)

def _get_sheet():
    # Sheet configuration via secrets or env vars
    try:
        from streamlit import secrets
        sheet_name = secrets["gspread"]["sheet_name"]
        worksheet = secrets["gspread"].get("worksheet", "Responses")
    except Exception:
        sheet_name = os.environ.get("GSPREAD_SHEET_NAME")
        worksheet = os.environ.get("GSPREAD_WORKSHEET", "Responses")
        if not sheet_name:
            raise RuntimeError(
                "Missing sheet name. Provide st.secrets['gspread']['sheet_name'] or env GSPREAD_SHEET_NAME."
            )

    client = _get_client()
    sh = client.open(sheet_name)
    try:
        ws = sh.worksheet(worksheet)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet, rows=1000, cols=50)
        # create headers on first row
        ws.append_row(["timestamp_utc"])
    return ws

def append_to_google_sheet(payload: Dict[str, Any]) -> None:
    ws = _get_sheet()
    # Ensure header columns exist and align
    headers = ws.row_values(1)
    # Add any missing keys as new columns
    new_cols = [k for k in payload.keys() if k not in headers]
    if new_cols:
        ws.resize(rows=ws.row_count, cols=max(len(headers) + len(new_cols), ws.col_count))
        headers = headers + new_cols
        ws.update(f"A1:{gspread.utils.rowcol_to_a1(1, len(headers))}", [headers])

    # Build row in header order
    row = [payload.get(h, "") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")

def healthcheck_google_sheet() -> Tuple[bool, str]:
    try:
        ws = _get_sheet()
        _ = ws.title
        return True, "ok"
    except Exception as e:
        return False, str(e)
