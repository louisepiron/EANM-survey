# Quick Booth Survey (Streamlit)

A touch-friendly Streamlit app for micro-interviews and a 60–90s survey at your EANM booth. Saves responses to Google Sheets.

## Features
- Step-by-step flow with branching for "already familiar" vs. "first time"
- Large touch targets, minimal chrome for iPad kiosk use
- Google Sheets storage, headers auto-expand to new fields
- Staff initials captured via URL param `?staff=LP` or field
- Message testing, content preferences, perception attributes

## Quick Start

### 1) Create a Google Sheet
- Create a spreadsheet, e.g., `EANM Booth Survey`.
- Add a worksheet named `Responses` (or keep default; the app will create it if missing).

### 2) Service Account credentials
- In Google Cloud Console, create a Service Account with access to Google Sheets API.
- Generate a JSON key.
- Share your spreadsheet with the service account email (Editor access).

### 3) Deploy (Streamlit Community Cloud)
- Fork or upload these files to a GitHub repo.
- On [Streamlit Cloud](https://share.streamlit.io), create a new app pointing to `app.py`.
- In App Settings → Secrets, add:

```toml
# Example of Streamlit secrets (paste this in Streamlit → Settings → Secrets)
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\\nYOUR-KEY\\n-----END PRIVATE KEY-----\\n"
client_email = "your-sa@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

[gspread]
sheet_name = "EANM Booth Survey"
worksheet = "Responses"
```

> Alternatively set env vars `GCP_SERVICE_ACCOUNT_JSON`, `GSPREAD_SHEET_NAME`, `GSPREAD_WORKSHEET`.

### 4) Test locally (optional)

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 5) Kiosk mode on iPad
- Open the app URL in Safari.
- Settings → Accessibility → Guided Access → On.
- Triple-press side button to start Guided Access, disable hardware buttons.
- Display & Brightness → Auto-Lock → Never.
- Enable Focus/Do Not Disturb during show hours.

### 6) Use staff initials
- Append `?staff=XX` to the URL for the person on duty, e.g., `https://your-app.streamlit.app/?staff=LP`.

## Customization
- Replace the message test statements in `app.py` (page 4).
- Add/remove perception attributes in page 2.
- Add your logo image and swap in `st.image("assets/logo.png", width=64)` in `big_header()`.

## Offline note
Streamlit requires an internet connection. If venue Wi‑Fi is unreliable, print QR codes to a backup Typeform/Google Form, or host the app on a local hotspot with a stable uplink.

## Privacy
- The app captures no PII unless the visitor opts in with an email.
- Consent is required to submit. Update language to match your privacy policy and retention period.
