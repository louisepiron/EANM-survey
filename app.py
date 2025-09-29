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

      /* Hide Streamlit default chrome for kiosk-like experience */
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
        font-size: 2.2rem; /* bigger title to visually match a ~64px logo */
        margin: 0;
        line-height: 1.1;
      }}

      /* Remove card boxes; use clean layout with light dividers */
      .title {{
          font-weight: 750;
          font-size: 1.15rem;
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


def go_next():
    st.session_state.page += 1


def go_back():
    st.session_state.page = max(0, st.session_state.page - 1)


def big_header():
    with st.container():
        st.markdown('<div class="brand-header">', unsafe_allow_html=True)
        col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
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

# Page 0 — Segmenting (use forms to avoid double-click and accidental submits)
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
        next_btn = st.form_submit_button("Next ➜")
        if next_btn:
            missing = validate_required({"Role": role, "Region": region})
            if missing:
                st.toast("Please select your Role and Region.", icon="⚠️")
            else:
                st.session_state.answers.update({"role": role, "region": region})
                go_next()

# Page 1 — Familiarity (updated wording and picklist)
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
            go_back()
        elif next_btn:
            st.session_state.answers["familiarity"] = fam
            go_next()

# Page 2 — Known vs first-time branching
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
                key="solutions",
            )
            st.markdown('<hr class="divider" />', unsafe_allow_html=True)

            st.markdown('<div class="title">How would you describe the IBA brand?</div>', unsafe_allow_html=True)
            st.caption("Drag and drop to rank from 1 (most representative) to 7 (least).")
            # Drag-and-drop ranking with fallback
            default_attrs = [
                "Reliable",
                "Innovative",
                "Efficient",
                "Supportive",
                "Trusted Partner",
                "Flexible",
                "Expert-Led",
            ]
            # Keep an order in session to preserve user rearrangement across reruns
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
                # Update session with new order
                if ranked and ranked != st.session_state.brand_attrs_order:
                    st.session_state.brand_attrs_order = ranked
            except Exception:
                # Fallback: simple multiselect capturing tap order
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
                go_back()
            elif next_btn:
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
                    go_next()

    else:
        with st.form("form_page_2_first", clear_on_submit=False):
            st.markdown('<div class="title">What problem are you trying to solve right now?</div>', unsafe_allow_html=True)
            problem = st.text_input("Briefly describe (optional)", key="current_problem")
            st.markdown('<hr class="divider" />', unsafe_allow_html=True)
            cols = st.columns(2)
            back_btn = cols[0].form_submit_button("⬅ Back")
            next_btn = cols[1].form_submit_button("Next ➜")
            if back_btn:
                go_back()
            elif next_btn:
                st.session_state.answers.update({"current_problem": problem})
                go_next()

# Page 3 — Content consumption and formats
elif st.session_state.page == 3:
    with st.form("form_page_3", clear_on_submit=False):
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
            go_back()
        elif next_btn:
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
                go_next()

# Page 4 — Message test + likelihood + feedback
elif st.session_state.page == 4:
    with st.form("form_page_4", clear_on_submit=False):
        st.markdown('<div class="title">Which message resonates most?</div>', unsafe_allow_html=True)
        # Use selectbox with an empty first option to avoid preselect and prevent accidental auto-advance
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

        # Promote the likelihood sentence as a main title-level element
        st.markdown('<div class="title">How likely are you to recommend our content/products to a colleague?</div>', unsafe_allow_html=True)
        nps = st.slider("", 0, 10, 8, key="likelihood_recommend")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        # Promote the “One thing” sentence visually at same level
        st.markdown('<div class="title">One thing we could do to be more valuable to you (optional)</div>', unsafe_allow_html=True)
        one_thing = st.text_area("", height=80, key="improve_one_thing")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        cols = st.columns(2)
        back_btn = cols[0].form_submit_button("⬅ Back")
        next_btn = cols[1].form_submit_button("Next ➜")
        if back_btn:
            go_back()
        elif next_btn:
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
                go_next()

# Page 5 — Submit (consent statement + opt-out)
elif st.session_state.page == 5:
    with st.form("form_page_5", clear_on_submit=False):
        st.markdown('<div class="title">Stay in touch</div>', unsafe_allow_html=True)
        st.write(
            "By submitting this form you consent to the processing of your responses for research and personalization purposes."
        )
        email = st.text_input("Work email (optional)", key="email")
        do_not_contact = st.checkbox("I don't want to receive relevant content updates in the future", value=False, key="do_not_contact")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        # Staff initials field only if not provided via URL
        staff = st.text_input(
            "Staff initials (optional)",
            value=st.session_state.answers.get("staff_initials", ""),
            key="staff_initials_input",
        )

        cols = st.columns(2)
        back_btn = cols[0].form_submit_button("⬅ Back")
        submit_btn = cols[1].form_submit_button("Submit ✅")
        if back_btn:
            go_back()
        elif submit_btn:
            answers = st.session_state.answers.copy()
            answers.update(
                {
                    # Consent is implicit by submission per your request
                    "consent": True,
                    "email": email.strip(),
                    "do_not_contact": do_not_contact,
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
                go_next()
            except Exception as e:
                st.error(f"Submission failed: {e}")
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
