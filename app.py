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
# Brand configuration (solid colors, no gradients)
# ----------------------------
BRAND_PRIMARY = "#69BE28"   # Green
BRAND_NEUTRAL = "#808691"   # Neutral gray for accents
DIVIDER_COLOR = "#E6E8EB"   # Light grey divider
FONT_STACK = "'Simplon Norm', Arial, sans-serif"
LOGO_PATH = "assets/logo.png"  # Place your logo file here (PNG)

# ----------------------------
# Global styles (branding)
# ----------------------------
st.markdown(
    f"""
    <style>
      html, body, [class*="css"] {{
        font-family: {FONT_STACK} !important;
        color: #1c1c1c;
      }}

      /* Hide Streamlit chrome and badges */
      [data-testid="stToolbar"] {{ display: none !important; }}
      [data-testid="stDecoration"] {{ display: none !important; }}
      [data-testid="viewerBadge"] {{ display: none !important; }}
      header {{ visibility: hidden; }}
      #MainMenu {{ visibility: hidden; }}
      footer {{ visibility: hidden; }}

      .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 1rem;
      }}

      /* Branded header bar (solid color) */
      .brand-header {{
        background: {BRAND_PRIMARY};
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: white;
      }}
      .brand-title {{
        font-weight: 850;
        font-size: 2.8rem; /* large title to match ~64px logo height */
        margin: 0;
        line-height: 1.05;
      }}

      /* Section titles and subtle text */
      .title {{
          font-weight: 750;
          font-size: 1.35rem;
          margin: 0 0 0.5rem 0;
          color: #1c1c1c;
      }}
      .subtle {{
          color: {BRAND_NEUTRAL};
      }}
      hr.divider {{
        border: none;
        border-top: 1px solid {DIVIDER_COLOR};
        margin: 10px 0 14px 0;
      }}

      /* BUTTONS — force solid green (covers primary/secondary/form buttons) */
      .stButton > button,
      .stForm .stButton > button,
      button,
      [data-testid="baseButton-secondary"],
      [data-testid="baseButton-primary"] {{
          height: 56px;
          font-size: 1.05rem;
          border-radius: 10px;
          background-color: {BRAND_PRIMARY} !important;
          color: #ffffff !important;
          border: 1px solid {BRAND_PRIMARY} !important;
      }}
      .stButton > button:hover,
      .stForm .stButton > button:hover,
      button:hover,
      [data-testid="baseButton-secondary"]:hover,
      [data-testid="baseButton-primary"]:hover {{
          filter: brightness(0.98);
      }}
      .stButton > button:disabled,
      .stForm .stButton > button:disabled {{
          opacity: 0.6 !important;
      }}

      /* ANSWER ZONES: light gray by default, green when focused/active */

      /* Select and Multiselect (BaseWeb Select) */
      div[data-baseweb="select"] > div {{
        border: 2px solid {DIVIDER_COLOR} !important;     /* default light gray */
        border-radius: 10px !important;
        transition: border-color 120ms ease-in-out;
      }}
      div[data-baseweb="select"]:focus-within > div,
      div[data-baseweb="select"][aria-expanded="true"] > div {{
        border-color: {BRAND_PRIMARY} !important;          /* green when focused/open */
      }}

      /* Text input */
      .stTextInput > div > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 2px 8px !important;
        transition: border-color 120ms ease-in-out;
      }}
      .stTextInput > div > div:focus-within {{
        border-color: {BRAND_PRIMARY} !important;
      }}

      /* Text area */
      .stTextArea > div > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 2px 8px !important;
        transition: border-color 120ms ease-in-out;
      }}
      .stTextArea > div > div:focus-within {{
        border-color: {BRAND_PRIMARY} !important;
      }}

      /* Radio group container */
      .stRadio > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
        transition: border-color 120ms ease-in-out;
      }}
      .stRadio > div:focus-within {{
        border-color: {BRAND_PRIMARY} !important;
      }}

      /* Drag-and-drop list items (light grey default; green when selected/dragging) */
      /* The SortableJS library adds these classes during interaction */
      ul.sortable li,
      .sortable li,
      li.sortable-item {{
        background: #F5F6F7 !important;                    /* light grey */
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        margin-bottom: 8px !important;
        list-style: none !important;
      }}
      /* Chosen/dragging/ghost states -> turn green */
      li.sortable-chosen,
      li.sortable-ghost,
      li.sortable-drag {{
        background: #E8F6DC !important;                   /* light green fill */
        border-color: {BRAND_PRIMARY} !important;         /* green border */
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


def navigate(delta: int):
    """Robust navigation that avoids 'double click' by forcing a fresh rerun."""
    st.session_state.page = max(0, st.session_state.page + delta)
    st.session_state["_nav_event_at"] = datetime.utcnow().isoformat()
    st.rerun()


def big_header():
    with st.container():
        st.markdown('<div class="brand-header">', unsafe_allow_html=True)
        col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
        with col_logo:
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

# Optional staff initials via URL
staff_initials = get_query_param("staff", "")
if staff_initials:
    st.session_state.answers["staff_initials"] = staff_initials

# Progress
st.progress(min(st.session_state.page / 6.0, 1.0))

# Page 0
if st.session_state.page == 0:
    with st.form("form_page_0", clear_on_submit=False):
        st.markdown('<div class="title">Tell us about you</div>', unsafe_allow_html=True)
        role = st.selectbox(
            "Role",
            ["", "Physician", "Medical Physicist", "Researcher", "Industry", "Radiopharmacist", "Other"],
            index=0,
            key="role",
        )
        region = st.selectbox(
            "Region",
            ["", "EU", "North America", "LATAM", "APAC", "Middle East", "Africa"],
            index=0,
            key="region",
        )
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        cols = st.columns(2)
        back_btn = cols[0].form_submit_button("⬅ Back")
        next_btn = cols[1].form_submit_button("Next ➜")
        if back_btn:
            navigate(-1)
        if next_btn:
            missing = validate_required({"Role": role, "Region": region})
            if missing:
                st.toast("Please select your Role and Region.", icon="⚠️")
            else:
                st.session_state.answers.update({"role": role, "region": region})
                navigate(+1)

# Page 1
elif st.session_state.page == 1:
    with st.form("form_page_1", clear_on_submit=False):
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
            key="familiarity",
        )
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        cols = st.columns(2)
        back_btn = cols[0].form_submit_button("⬅ Back")
        next_btn = cols[1].form_submit_button("Next ➜")
        if back_btn:
            navigate(-1)
        if next_btn:
            st.session_state.answers["familiarity"] = fam
            navigate(+1)

# Page 2
elif st.session_state.page == 2:
    fam = st.session_state.answers.get("familiarity", "")
    is_first_time = fam == "It's the first time I hear about IBA"

    if not is_first_time:
        with st.form("form_page_2_known", clear_on_submit=False):
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
                key="first_touch",
            )
            st.markdown('<hr class="divider" />', unsafe_allow_html=True)

            st.markdown('<div class="title">Have you purchased any of the following solutions?</div>', unsafe_allow_html=True)
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
                    "Integralab®",
                    "Cylcone® 18/9",
                ],
                key="solutions",
            )
            st.markdown('<hr class="divider" />', unsafe_allow_html=True)

            st.markdown('<div class="title">How would you describe the IBA brand?</div>', unsafe_allow_html=True)
            st.caption("Drag and drop to rank from 1 (most representative) to 7 (least).")
            default_attrs = [
                "Reliable",
                "Innovative",
                "Efficient",
                "Supportive",
                "Trusted Partner",
                "Flexible",
                "Expert-Led",
            ]
            if "brand_attrs_order" not in st.session_state:
                st.session_state.brand_attrs_order = default_attrs

            ranked = None
            try:
                from streamlit_sortables import sort_items  # pip install streamlit-sortables
                ranked = sort_items(
                    st.session_state.brand_attrs_order,
                    direction="vertical",
                    key="brand_sort",
                )
                if ranked and ranked != st.session_state.brand_attrs_order:
                    st.session_state.brand_attrs_order = ranked
            except Exception:
                ranked = st.multiselect(
                    "If drag-and-drop is unavailable, tap attributes in order (top = most representative)",
                    default_attrs,
                    default=default_attrs,
                    key="brand_attrs_fallback",
                    help="Your selection order will be recorded as the ranking.",
                )
                st.session_state.brand_attrs_order = ranked

            st.markdown('<hr class="divider" />', unsafe_allow_html=True)
            cols = st.columns(2)
            back_btn = cols[0].form_submit_button("⬅ Back")
            next_btn = cols[1].form_submit_button("Next ➜")
            if back_btn:
                navigate(-1)
            if next_btn:
                missing = validate_required({"First touchpoint": first_touch})
                if missing:
                    st.toast("Please complete the required fields.", icon="⚠️")
                else:
                    st.session_state.answers.update(
                        {
                            "first_touch": first_touch,
                            "solutions": solutions,
                            "brand_attributes_ranked": st.session_state.brand_attrs_order,
                        }
                    )
                    navigate(+1)

    else:
        with st.form("form_page_2_first", clear_on_submit=False):
            st.markdown('<div class="title">What problem are you trying to solve right now?</div>', unsafe_allow_html=True)
            problem = st.text_input("Briefly describe (optional)", key="current_problem")
            st.markdown('<hr class="divider" />', unsafe_allow_html=True)
            cols = st.columns(2)
            back_btn = cols[0].form_submit_button("⬅ Back")
            next_btn = cols[1].form_submit_button("Next ➜")
            if back_btn:
                navigate(-1)
            if next_btn:
                st.session_state.answers.update({"current_problem": problem})
                navigate(+1)

# Page 3
elif st.session_state.page == 3:
    with st.form("form_page_3", clear_on_submit=False):
        st.markdown('<div class="title">Through which channels do you consume professional content?</div>', unsafe_allow_html=True)
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
            key="channels",
        )
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

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
            key="formats",
        )
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        st.markdown('<div class="title">Preferred video length</div>', unsafe_allow_html=True)
        video_len = st.radio("", ["<60s", "1–3 min", "3–6 min", "6–12 min"], index=1, horizontal=True, key="video_length")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        cols = st.columns(2)
        back_btn = cols[0].form_submit_button("⬅ Back")
        next_btn = cols[1].form_submit_button("Next ➜")
        if back_btn:
            navigate(-1)
        if next_btn:
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
                navigate(+1)

# Page 4
elif st.session_state.page == 4:
    with st.form("form_page_4", clear_on_submit=False):
        st.markdown('<div class="title">Which message resonates most?</div>', unsafe_allow_html=True)
        message = st.selectbox(
            "Pick one",
            [
                "",
                "Empowering precision in nuclear medicine workflows—simplified, standardized, and scalable.",
                "From radiopharmaceutical preparation to clinical reporting—accelerated, reliable outcomes you can trust.",
                "Driving clinical impact through trusted radiopharma solutions—confidence at every step.",
            ],
            index=0,
            key="message_choice",
        )
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        st.markdown('<div class="title">How likely are you to recommend our content/products to a colleague?</div>', unsafe_allow_html=True)
        nps = st.slider("", 0, 10, 8, key="likelihood_recommend")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        st.markdown('<div class="title">One thing we could do to be more valuable to you (optional)</div>', unsafe_allow_html=True)
        one_thing = st.text_area("", height=80, key="improve_one_thing")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        cols = st.columns(2)
        back_btn = cols[0].form_submit_button("⬅ Back")
        next_btn = cols[1].form_submit_button("Next ➜")
        if back_btn:
            navigate(-1)
        if next_btn:
            if message.strip() == "":
                st.toast("Please choose a message.", icon="⚠️")
            else:
                st.session_state.answers.update(
                    {
                        "message_choice": message,
                        "likelihood_recommend": nps,
                        "improve_one_thing": one_thing,
                    }
                )
                navigate(+1)

# Page 5
elif st.session_state.page == 5:
    with st.form("form_page_5", clear_on_submit=False):
        st.markdown('<div class="title">Stay in touch</div>', unsafe_allow_html=True)
        st.write("By submitting this form you consent to the processing of your responses for research and personalization purposes.")
        email = st.text_input("Work email (optional)", key="email")
        do_not_contact = st.checkbox("I don't want to receive relevant content updates in the future", value=False, key="do_not_contact")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        staff = st.text_input(
            "Staff initials (optional)",
            value=st.session_state.answers.get("staff_initials", ""),
            key="staff_initials_input",
        )

        cols = st.columns(2)
        back_btn = cols[0].form_submit_button("⬅ Back")
        submit_btn = cols[1].form_submit_button("Submit ✅")
        if back_btn:
            navigate(-1)
        if submit_btn:
            answers = st.session_state.answers.copy()
            answers.update(
                {
                    "consent": True,
                    "email": email.strip(),
                    "do_not_contact": do_not_contact,
                    "staff_initials": staff.strip(),
                    "timestamp_utc": datetime.utcnow().isoformat(),
                }
            )
            for k in ["channels", "formats", "solutions", "brand_attributes_ranked"]:
                if k in answers and isinstance(answers[k], list):
                    answers[k] = ", ".join(answers[k])

            try:
                append_to_google_sheet(answers)
                st.session_state.submitted = True
                navigate(+1)
            except Exception as e:
                st.error(f"Submission failed: {e}")
                st.info("Please check your internet connection and try again.")

# Thank you
else:
    st.success("Thank you! Your responses have been recorded.")
    st.button(
        "Start another response ↺",
        on_click=lambda: [
            st.session_state.update({"page": 0, "answers": {}, "submitted": False, "error_msg": ""}),
            st.rerun(),
        ],
    )
