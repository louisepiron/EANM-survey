import os
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st

from utils.g_sheets import append_to_google_sheet

# ----------------------------
# Basic configuration
# ----------------------------
st.set_page_config(
    page_title="IBA RadioPharma Solutions Quick Brand Perception survey",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Brand configuration
# ----------------------------
BRAND_PRIMARY = "#69BE28"   # Green
BRAND_SECONDARY = "#B8D587" # Light green (used sparingly as neutral accent)
BRAND_NEUTRAL = "#808691"   # Neutral gray
FONT_STACK = "'Simplon Norm', Arial, sans-serif"
LOGO_PATH = "assets/logo.png"  # Place your logo file here (PNG)

# ----------------------------
# Global styles (branding) - solid colors only
# ----------------------------
st.markdown(
    f"""
    <style>
      :root {{
        --brand-primary: {BRAND_PRIMARY};
        --brand-secondary: {BRAND_SECONDARY};
        --brand-neutral: {BRAND_NEUTRAL};
      }}

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

      /* Branded header bar (solid color, no gradient) */
      .brand-header {{
        background: {BRAND_PRIMARY};
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 16px;
        color: white;
      }}
      .brand-title {{
        font-weight: 800;
        font-size: 1.6rem; /* bigger title per request */
        margin: 0;
        line-height: 1.25;
      }}

      /* Cards for questions */
      .question-card {{
          background: #FFFFFF;
          border: 1px solid rgba(128,134,145,0.20);
          border-radius: 12px;
          padding: 18px 16px;
          margin-bottom: 12px;
          box-shadow: 0 1px 2px rgba(0,0,0,0.04);
      }}
      .title {{
          font-weight: 700;
          font-size: 1.1rem;
          margin-bottom: 0.25rem;
          color: #1c1c1c;
      }}
      .subtitle {{
          color: {BRAND_NEUTRAL};
          font-size: 0.95rem;
          margin-bottom: 0.75rem;
      }}

      /* Buttons (solid primary) */
      .stButton > button {{
          height: 56px;
          font-size: 1.05rem;
          border-radius: 10px;
          border: 1px solid rgba(0,0,0,0.04);
          background: {BRAND_PRIMARY} !important;
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

      /* Progress bar brand (solid) */
      .stProgress > div > div > div {{
          background: {BRAND_PRIMARY} !important;
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
            # Show logo if present; no placeholder if missing (prevents empty white box)
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=64)
        with col_title:
            st.markdown(
                '<p class="brand-title">IBA RadioPharma Solutions Quick Brand Perception survey</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


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

# Optional staff initials via URL, no UI box if provided
staff_initials = get_query_param("staff", "")
if staff_initials:
    st.session_state.answers["staff_initials"] = staff_initials

# Simple progress indicator
st.progress(min(st.session_state.page / 6.0, 1.0))

# Page 0 — Segmenting
if st.session_state.page == 0:
    with st.container():
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">Tell us about you</div>', unsafe_allow_html=True)
        role = st.selectbox(
            "Role",
            ["", "Physician", "Medical Physicist", "Researcher", "Industry", "Radiopharmacist", "Other"],
            index=0,
        )
        region = st.selectbox(
            "Region",
            ["", "EU", "North America", "LATAM", "APAC", "Middle East", "Africa"],
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

# Page 1 — Familiarity (updated wording and picklist)
elif st.session_state.page == 1:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">How familiar are you with the IBA brand?</div>', unsafe_allow_html=True)
    fam = st.selectbox(
        "Select one",
        [
            "I'm a current customer",
            "I've been a customer",
            "I'm not a customer but I'm considering purchasing a product",
            "I'm familiar with IBA but don't have / plan to buy a product",
            "It's the first time I hear about IBA",
        ],
        index=2,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1])
    if cols[0].button("⬅ Back"):
        prev_page()
    if cols[1].button("Next ➜"):
        st.session_state.answers["familiarity"] = fam
        next_page()

# Page 2 — Known vs first-time branching
elif st.session_state.page == 2:
    fam = st.session_state.answers.get("familiarity", "")
    is_first_time = fam == "It's the first time I hear about IBA"

    if not is_first_time:
        # Known branch
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">Where did you first hear about us?</div>', unsafe_allow_html=True)
        first_touch = st.selectbox(
            "Choose one",
            [
                "",
                "Colleague / Friend",
                "Congress",
                "IBA website",
                "Search (Google)",
                "Email newsletter",
                "LinkedIn",
                "Instagram",
                "Other",
            ],
            index=0,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">Which of our solutions have you used or know best?</div>', unsafe_allow_html=True)
        solutions = st.multiselect(
            "Select all that apply",
            [
                "Cyclone® Key",
                "Cyclone® Kiube",
                "Cyclone® IKON",
                "Cyclone® 30XP",
                "Cyclone® 70",
                "Synthera®",
                "Cassy®",
            ],
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">How would you describe the IBA brand? (rank by tapping in order)</div>', unsafe_allow_html=True)
        st.caption("Select attributes in order from most to least representative.")
        brand_attrs = st.multiselect(
            "Select in order (top = most representative)",
            [
                "Innovative",
                "Trustworthy",
                "Clinically impactful",
                "Reliable",
                "Easy to work with",
                "Evidence-based",
                "Premium quality",
                "Good value for money",
            ],
            help="Your selection order will be recorded as the ranking.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        cols = st.columns([1, 1])
        if cols[0].button("⬅ Back"):
            prev_page()
        if cols[1].button("Next ➜"):
            missing = validate_required({"First touchpoint": first_touch})
            # 'solutions' and 'brand_attrs' can be optional; make them required if you prefer:
            if missing:
                st.toast("Please complete the required fields.", icon="⚠️")
            else:
                st.session_state.answers.update(
                    {
                        "first_touch": first_touch,
                        "solutions": solutions,
                        "brand_attributes_ranked": brand_attrs,
                    }
                )
                next_page()

    else:
        # First-time branch
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">What problem are you trying to solve right now?</div>', unsafe_allow_html=True)
        problem = st.text_input("Briefly describe (optional)")
        st.markdown("</div>", unsafe_allow_html=True)

        cols = st.columns([1, 1])
        if cols[0].button("⬅ Back"):
            prev_page()
        if cols[1].button("Next ➜"):
            st.session_state.answers.update({"current_problem": problem})
            next_page()

# Page 3 — Content consumption and formats
elif st.session_state.page == 3:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Where do you consume professional content?</div>', unsafe_allow_html=True)
    channels = st.multiselect(
        "Select all that apply",
        [
            "LinkedIn",
            "Instagram",
            "YouTube",
            "Industry association websites",
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
            "Short video (<2 min) quick tips",
            "Video demos (3–6 min)",
            "Case studies",
            "Protocols / how-tos (step-by-step guides)",
            "Webinars (live or on-demand)",
            "White papers / technical briefs",
            "Email digest / newsletter",
            "Podcasts",
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

# Page 4 — Message test + outcome
elif st.session_state.page == 4:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Which message resonates most?</div>', unsafe_allow_html=True)
    message = st.radio(
        "Pick one",
        [
            "Empowering precision in nuclear medicine workflows—simplified, standardized, and scalable.",
            "From radiopharmaceutical preparation to clinical reporting—accelerated, reliable outcomes you can trust.",
            "Driving clinical impact through trusted radiopharma solutions—confidence at every step.",
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

# Page 5 — Stay in touch (merged consent + contact)
elif st.session_state.page == 5:
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Stay in touch</div>', unsafe_allow_html=True)

    consent = st.checkbox(
        "I consent to the processing of my responses for research and personalization and agree to be contacted with relevant content.",
        value=False,
    )
    email = st.text_input("Work email (optional)")

    # Staff initials field only if not provided via URL
    staff = st.text_input(
        "Staff initials (optional)",
        value=st.session_state.answers.get("staff_initials", ""),
    )
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1])
    if cols[0].button("⬅ Back"):
        prev_page()

    if cols[1].button("Submit ✅"):
        if not consent:
            st.toast("Please check the consent box to submit.", icon="⚠️")
        else:
            answers = st.session_state.answers.copy()
            answers.update(
                {
                    "consent": consent,
                    "email": email.strip(),
                    "staff_initials": staff.strip(),
                    "timestamp_utc": datetime.utcnow().isoformat(),
                }
            )

            # Flatten lists
            for k in ["channels", "formats", "solutions", "brand_attributes_ranked"]:
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

# Thank you page
else:
    st.success("Thank you! Your responses have been recorded.")
    st.button(
        "Start another response ↺",
        on_click=lambda: [
            st.session_state.update({"page": 0, "answers": {}, "submitted": False, "error_msg": ""})
        ],
    )
