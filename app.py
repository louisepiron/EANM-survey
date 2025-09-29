import os
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st

from utils.g_sheets import append_to_google_sheet, healthcheck_google_sheet

# ----------------------------
# Basic configuration
# ----------------------------
st.set_page_config(
    page_title="Quick Booth Survey",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Brand configuration
# ----------------------------
BRAND_PRIMARY = "#69BE28"   # Green
BRAND_SECONDARY = "#B8D587" # Light green
BRAND_NEUTRAL = "#808691"   # Neutral gray
BRAND_GRADIENT = f"linear-gradient(135deg, {BRAND_PRIMARY} 0%, {BRAND_SECONDARY} 100%)"
FONT_STACK = "'Simplon Norm', Arial, sans-serif"
LOGO_PATH = "assets/logo.png"  # Place your logo file here (PNG)

# ----------------------------
# Global styles (branding)
# ----------------------------
st.markdown(
    f"""
    <style>
      :root {{
        --brand-primary: {BRAND_PRIMARY};
        --brand-secondary: {BRAND_SECONDARY};
        --brand-neutral: {BRAND_NEUTRAL};
      }}

      /* Optional: Load Simplon Norm if you add a webfont file (see README)
      @font-face {{
        font-family: 'Simplon Norm';
        src: url('assets/SimplonNorm.woff2') format('woff2');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
      }}
      */

      html, body, [class*="css"] {{
        font-family: {FONT_STACK} !important;
        color: #1c1c1c;
      }}

      /* Hide Streamlit default chrome for kiosk-like experience */
      header {{ visibility: hidden; }}
      #MainMenu {{ visibility: hidden; }}
      footer {{ visibility: hidden; }}

      .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 1rem;
      }}

      /* Branded header bar */
      .brand-header {{
        background: {BRAND_GRADIENT};
        border-radius: 14px;
        padding: 10px 14px;
        margin-bottom: 14px;
        color: white;
      }}
      .brand-title {{
        font-weight: 700;
        font-size: 1.25rem;
        margin: 0 0 4px 0;
        line-height: 1.2;
      }}
      .brand-caption {{
        font-size: 0.95rem;
        opacity: 0.95;
        margin: 0;
      }}

      /* Cards for questions */
      .question-card {{
          background: #FFFFFF;
          border: 1px solid rgba(128,134,145,0.20);
          border-radius: 14px;
          padding: 20px 16px;
          margin-bottom: 12px;
          box-shadow: 0 1px 2px rgba(0,0,0,0.04);
      }}
      .title {{
          font-weight: 700;
          font-size: 1.15rem;
          margin-bottom: 0.25rem;
          color: #1c1c1c;
      }}
      .subtitle {{
          color: {BRAND_NEUTRAL};
          font-size: 0.95rem;
          margin-bottom: 0.75rem;
      }}

      /* Buttons */
      .stButton > button {{
          height: 56px;
          font-size: 1.05rem;
          border-radius: 12px;
          border: 1px solid rgba(0,0,0,0.04);
          background: {BRAND_GRADIENT} !important;
          color: white !important;
      }}
      .stButton > button:hover {{
          filter: brightness(0.98);
      }}

      /* Inputs and touch targets */
      .stTextInput input, .stSelectbox, .stMultiSelect, .stTextArea textarea {{
          font-size: 1.05rem !important;
      }}
      .stRadio label, .stSelectbox label, .stMultiSelect label, .stTextInput label, .stTextArea label {{
          font-weight: 600;
          color: #1c1c1c;
      }}
      input[type="radio"], input[type="checkbox"] {{
          accent-color: {BRAND_PRIMARY};
      }}

      /* Slider + progress accent */
      .stSlider [role="slider"] {{
          border-color: {BRAND_PRIMARY} !important;
      }}
      .stSlider [data-baseweb="slider"] > div > div {{
          background: rgba(105,190,40,0.25) !important;
      }}
      .stSlider [data-baseweb="slider"] .css-14xtw13 {{
          background: {BRAND_PRIMARY} !important;
      }}

      /* Progress bar brand */
      .stProgress > div > div > div {{
          background: {BRAND_GRADIENT} !important;
      }}

      /* Links (e.g., privacy policy) */
      a {{
        color: {BRAND_PRIMARY};
        text-decoration: none;
      }}
      a:hover {{
        text-decoration: underline;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Helpers
# ----------------------------
def get_query_param(name: str, default: str = "") -> str:
    # Works with newer and older Streamlit
    try:
        return st.query_params.get(name, default)
    except Exception:
        qp = st.experimental_get_query_params()
        return qp.get(name, [default])[0] if qp else default


def init_state():
    defaults = {"page": 0, "answers": {}, "submitted": False, "error_msg": ""}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def next_page():
    st.session_state.page += 1


def prev_page():
    st.session_state.page = max(0, st.session_state.page - 1)


def big_header():
    with st.container():
        st.markdown('<div class="brand-header">', unsafe_allow_html=True)
        col_logo, col_title = st.columns([1, 8])
        with col_logo:
            try:
                st.image(LOGO_PATH, width=64)
            except Exception:
                st.write(" ")
        with col_title:
            st.markdown('<p class="brand-title">Quick Booth Survey</p>', unsafe_allow_html=True)
            st.markdown('<p class="brand-caption">60–90 seconds; your input helps us improve our content and products.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def likert_row(title: str, key: str, min_val=1, max_val=5, help_txt: str = "") -> int:
    with st.container():
        st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)
        if help_txt:
            st.caption(help_txt)
        val = st.slider("", min_value=min_val, max_value=max_val, value=int((min_val + max_val) / 2), key=key)
    return val


def validate_required(fields: Dict[str, Any]) -> List[str]:
    missing = []
    for k, v in fields.items():
        if v is None:
            missing.append(k)
        elif isinstance(v, str) and v.strip() == "":
            missing.append(k)
        elif isinstance(v, list) and len(v) == 0:
            missing.append(k)
    return missing


# ----------------------------
# App flow
# ----------------------------
init_state()
big_header()

staff_initials = get_query_param("staff", "")
if staff_initials:
    st.session_state.answers["staff_initials"] = staff_initials

with st.expander("Connection status", expanded=False):
    ok, msg = healthcheck_google_sheet()
    st.write("Sheets:", "✅ Connected" if ok else f"⚠️ {msg}")

st.progress(min(st.session_state.page / 6.0, 1.0))

if st.session_state.page == 0:
    with st.container():
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">Tell us about you</div>', unsafe_allow_html=True)
        role = st.selectbox(
            "Role",
            ["", "Physician", "Technologist", "Physicist", "Researcher", "Industry", "Other"],
            index=0,
        )
        region = st.selectbox(
            "Region",
            ["", "EU", "UK", "North America", "LATAM", "APAC", "Other"],
            index=0,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Next ➜"):
        missing = validate_required({"Role": role, "Region": region})
        if missing:
            st.toast("Please select your Role and Region.", icon="⚠️")
        else:
            st.session_state.answers.update({"role": role, "region": region})
            next_page()

elif st.session_state.page == 1:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">How familiar are you with our brand?</div>', unsafe_allow_html=True)
    fam = st.radio(
        "Select one",
        [
            "I'm a current customer",
            "I've used or evaluated",
            "I'm familiar with the brand",
            "First time hearing about you",
        ],
        index=1,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1])
    if cols[0].button("⬅ Back"):
        prev_page()
    if cols[1].button("Next ➜"):
        st.session_state.answers["familiarity"] = fam
        next_page()

elif st.session_state.page == 2:
    fam = st.session_state.answers.get("familiarity", "")
    is_known = fam in [
        "I'm a current customer",
        "I've used or evaluated",
        "I'm familiar with the brand",
    ]

    if is_known:
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">Where did you first hear about us?</div>', unsafe_allow_html=True)
        first_touch = st.selectbox(
            "Choose one",
            [
                "",
                "LinkedIn",
                "Conference",
                "Colleague recommendation",
                "Society website",
                "Search (Google)",
                "Email newsletter",
                "Other",
            ],
            index=0,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">Which of our solutions have you used or know best?</div>', unsafe_allow_html=True)
        solutions = st.text_input("List product(s) or feature(s)")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">How do you rate us on the following?</div>', unsafe_allow_html=True)
        innov = likert_row("Innovation", "likert_innov")
        clin = likert_row("Clinical impact", "likert_clin")
        ease = likert_row("Ease of use", "likert_ease")
        support = likert_row("Customer support", "likert_support")
        value = likert_row("Value for money", "likert_value")
        st.markdown("</div>", unsafe_allow_html=True)

        cols = st.columns([1, 1])
        if cols[0].button("⬅ Back"):
            prev_page()
        if cols[1].button("Next ➜"):
            missing = validate_required({"First touchpoint": first_touch, "Solutions": solutions})
            if missing:
                st.toast("Please complete the required fields.", icon="⚠️")
            else:
                st.session_state.answers.update(
                    {
                        "first_touch": first_touch,
                        "solutions": solutions,
                        "attr_innovation": innov,
                        "attr_clinical": clin,
                        "attr_ease": ease,
                        "attr_support": support,
                        "attr_value": value,
                    }
                )
                next_page()
    else:
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">Before today, had you heard of us?</div>', unsafe_allow_html=True)
        heard = st.radio("", ["Yes", "No", "Not sure"], index=2)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">What problem are you trying to solve right now?</div>', unsafe_allow_html=True)
        problem = st.text_input("Briefly describe")
        st.markdown("</div>", unsafe_allow_html=True)

        cols = st.columns([1, 1])
        if cols[0].button("⬅ Back"):
            prev_page()
        if cols[1].button("Next ➜"):
            st.session_state.answers.update(
                {
                    "heard_before": heard,
                    "current_problem": problem,
                }
            )
            next_page()

elif st.session_state.page == 3:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Where do you discover professional content?</div>', unsafe_allow_html=True)
    channels = st.multiselect(
        "Select all that apply",
        [
            "LinkedIn",
            "YouTube",
            "Society websites",
            "Email newsletters",
            "Webinars",
            "Podcasts",
            "X/Twitter",
            "ResearchGate",
            "Google",
            "Other",
        ],
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Preferred content formats</div>', unsafe_allow_html=True)
    formats = st.multiselect(
        "Select all that apply",
        [
            "<2-min quick tips",
            "3–6 min demos",
            "Case studies",
            "Protocols / how-tos",
            "Webinars",
            "White papers",
            "Email digest",
        ],
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Preferred video length</div>', unsafe_allow_html=True)
    video_len = st.radio("", ["<60s", "1–3 min", "3–6 min", "6–12 min"], index=1, horizontal=True)
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1])
    if cols[0].button("⬅ Back"):
        prev_page()
    if cols[1].button("Next ➜"):
        missing = validate_required({"Channels": channels, "Formats": formats, "Video length": video_len})
        if missing:
            st.toast("Please select at least one channel and format.", icon="⚠️")
        else:
            st.session_state.answers.update(
                {
                    "channels": channels,
                    "formats": formats,
                    "video_length": video_len,
                }
            )
            next_page()

elif st.session_state.page == 4:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Which message resonates most?</div>', unsafe_allow_html=True)
    message = st.radio(
        "Pick one",
        [
            "Delivering evidence-based nuclear medicine workflows, simplified.",
            "From protocol to report: faster, consistent results you can trust.",
            "Clinical impact first: tools that help you treat with confidence.",
        ],
        index=1,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Outcome</div>', unsafe_allow_html=True)
    nps = st.slider("How likely are you to recommend our content/products to a colleague?", 0, 10, 8)
    one_thing = st.text_area("One thing we could do to be more valuable to you (optional)", height=80)
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1])
    if cols[0].button("⬅ Back"):
        prev_page()
    if cols[1].button("Next ➜"):
        st.session_state.answers.update(
            {
                "message_choice": message,
                "likelihood_recommend": nps,
                "improve_one_thing": one_thing,
            }
        )
        next_page()

elif st.session_state.page == 5:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Stay in touch (optional)</div>', unsafe_allow_html=True)
    opt_in = st.radio("May we contact you with relevant content?", ["No", "Yes"], index=0, horizontal=True)
    email = ""
    if opt_in == "Yes":
        email = st.text_input("Work email")
    consent = st.checkbox(
        "I consent to the processing of my responses for research and personalization. See our Privacy Policy.",
        value=False,
    )
    staff = st.text_input("Staff initials (optional)", value=st.session_state.answers.get("staff_initials", ""))

    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1])
    if cols[0].button("⬅ Back"):
        prev_page()

    if cols[1].button("Submit ✅"):
        if not consent:
            st.toast("Consent is required to submit.", icon="⚠️")
        elif opt_in == "Yes" and (email.strip() == "" or "@" not in email):
            st.toast("Please enter a valid email or choose No.", icon="⚠️")
        else:
            answers = st.session_state.answers.copy()
            answers.update(
                {
                    "opt_in": opt_in,
                    "email": email.strip(),
                    "consent": consent,
                    "staff_initials": staff.strip(),
                    "timestamp_utc": datetime.utcnow().isoformat(),
                }
            )

            # Flatten lists
            for k in ["channels", "formats"]:
                if k in answers and isinstance(answers[k], list):
                    answers[k] = ", ".join(answers[k])

            try:
                append_to_google_sheet(answers)
                st.session_state.submitted = True
                next_page()
            except Exception as e:
                st.session_state.error_msg = f"Submission failed: {e}"
                st.error(st.session_state.error_msg)
                st.info("Please check your internet connection and try again.")

else:
    st.success("Thank you! Your responses have been recorded.")
    st.caption("Enjoy EANM. You can close this page or hand the iPad back to staff.")
    st.button(
        "Start another response ↺",
        on_click=lambda: [
            st.session_state.update({"page": 0, "answers": {}, "submitted": False, "error_msg": ""})
        ],
    )
