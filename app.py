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
# Global styles (clean CSS + semantic headings)
# ----------------------------
st.markdown(
    f"""
    <style>
      html, body, [class*="css"] {{
        font-family: {FONT_STACK} !important;
        color: #1c1c1c;
      }}

      /* Hide Streamlit/GitHub chrome and badges more aggressively */
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="viewerBadge"],
      [data-testid="stStatusWidget"],
      [data-testid="stHeaderActionMenu"] {{ display: none !important; }}
      header, #MainMenu, footer {{ display: none !important; }}

      /* Kill creator/viewer badges and any GitHub-branded fixed bits on all screens */
      [data-testid="viewerBadge"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [aria-label*="View source on GitHub"],
      a[aria-label*="GitHub"],
      a[href*="github.com"],
      svg[aria-label*="GitHub"],
      div[style*="position: fixed"]:has(a[href*="github.com"]),
      div[style*="position: sticky"]:has(a[href*="github.com"]) {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
      }}

      /* Extra mobile hardening: hide any GitHub/branding links or images on small screens */
      @media (max-width: 768px) {{
        a[href*="github.com"],
        a[href*="github.com"] img,
        a[aria-label*="GitHub"],
        img[alt*="GitHub"],
        svg[aria-label*="GitHub"],
        [aria-label*="View source on GitHub"],
        a[href*="streamlit.io"],
        a[href*="streamlit.io"] img,
        [data-testid*="Creator"],
        [data-testid*="creator"],
        [data-testid*="Badge"],
        [data-testid*="badge"] {{ display: none !important; }}
      }}

      .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 1rem;
      }}

      /* H1 form title bar (solid green), H1 text inside (1.6rem) */
      .brand-header {{
        background: {BRAND_PRIMARY};
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: white;
      }}
      /* Neutralize any auto-injected H1 sizing on dynamic Streamlit classes */
      .st-emotion-cache-10j6mrm h1 {{
        font-size: inherit !important;
        line-height: inherit !important;
      }}
      .brand-header h1 {{
        font-weight: 850;
        font-size: 1.6rem;
        margin: 0;
        line-height: 1.15;
      }}
      /* Vertically center logo and H1 */
      .brand-header [data-testid="column"] {{
        display: flex;
        align-items: center;
      }}
      .brand-header [data-testid="column"]:first-child img {{
        display: block;
        height: 64px;
        width: auto;
      }}
      .brand-header [data-testid="column"]:nth-child(2) h1 {{
        margin-left: 12px;
      }}

      /* H2 section/question titles */
      h2.section-title {{
        font-weight: 750;
        font-size: 1.45rem;
        margin: 0 0 0.5rem 0;
        color: #1c1c1c;
      }}

      /* Subtle text + dividers */
      .subtle {{ color: {BRAND_NEUTRAL}; }}
      hr.divider {{
        border: none;
        border-top: 1px solid {DIVIDER_COLOR};
        margin: 10px 0 14px 0;
      }}

      /* Buttons — force solid green (primary/secondary/base + form submit buttons) */
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
          width: auto !important;
          display: inline-flex !important;
          align-items: center;
          justify-content: center;
      }}
      .stButton > button:hover,
      .stForm .stButton > button:hover,
      button:hover,
      [data-testid="baseButton-secondary"]:hover,
      [data-testid="baseButton-primary"]:hover {{ filter: brightness(0.98); }}
      .stButton > button:disabled,
      .stForm .stButton > button:disabled {{ opacity: 0.6 !important; }}

      /* Default alignment rules (desktop) */
      [data-testid="stForm"] > div [data-testid="column"]:nth-child(2) .stButton > button {{
        margin-left: auto !important; /* push to the right */
        display: inline-flex !important;
      }}
      [data-testid="stForm"] > div [data-testid="column"]:first-child .stButton > button {{
        margin-right: auto !important;
        display: inline-flex !important;
      }}

      /* Robust fix: treat the button row (the columns parent) as a 2-col grid so it NEVER stacks,
         and align buttons to edges on all screen sizes */
      [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(.stButton) {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        column-gap: 0.75rem !important;
        align-items: end !important;
        width: 100% !important;
      }}
      [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(.stButton) [data-testid="column"] {{
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
      }}
      [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(.stButton) [data-testid="column"]:first-child .stButton {{
        text-align: left !important;
        width: 100% !important;
      }}
      [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(.stButton) [data-testid="column"]:last-child .stButton {{
        text-align: right !important;
        width: 100% !important;
      }}
      [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(.stButton) [data-testid="column"]:first-child .stButton > button {{
        float: left !important;
      }}
      [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(.stButton) [data-testid="column"]:last-child .stButton > button {{
        float: right !important;
      }}

      /* Ensure mobile keeps two-up (no stacking) */
      @media (max-width: 768px) {{
        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(.stButton) {{
          grid-template-columns: 1fr 1fr !important;
        }}
      }}

      /* Answer zones: light gray by default; green on focus/active */
      /* Select/Multiselect (BaseWeb Select) */
      div[data-baseweb="select"] > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        transition: border-color 120ms ease-in-out;
      }}
      div[data-baseweb="select"]:focus-within > div,
      div[data-baseweb="select"][aria-expanded="true"] > div {{ border-color: {BRAND_PRIMARY} !important; }}

      /* Text input */
      .stTextInput > div > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 2px 8px !important;
        transition: border-color 120ms ease-in-out;
      }}
      .stTextInput > div > div:focus-within {{ border-color: {BRAND_PRIMARY} !important; }}

      /* Text area */
      .stTextArea > div > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 2px 8px !important;
        transition: border-color 120ms ease-in-out;
      }}
      .stTextArea > div > div:focus-within {{ border-color: {BRAND_PRIMARY} !important; }}

      /* Radio group container and labels (wrap long sentences fully) */
      .stRadio > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
        transition: border-color 120ms ease-in-out;
      }}
      .stRadio > div:focus-within {{ border-color: {BRAND_PRIMARY} !important; }}
      .stRadio label {{
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        line-height: 1.3 !important;
      }}

      /* Sortable single list (ranking all attributes) */
      ul.sortable, .sortable {{
        background: #FFFFFF !important;
        border: 2px dashed {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 8px !important;
        list-style: none !important;
        counter-reset: rank;
      }}
      ul.sortable li,
      .sortable li,
      li.sortable-item {{
        background: #E8F6DC !important;                 /* green-tinted attribute items */
        border: 2px solid {BRAND_PRIMARY} !important;   /* green border */
        border-radius: 10px !important;
        padding: 10px 12px !important;
        margin-bottom: 8px !important;
        list-style: none !important;
        display: flex; align-items: center;
      }}
      /* numeric prefix 1., 2., 3., ... */
      ul.sortable li::before {{
        counter-increment: rank;
        content: counter(rank) ".";
        font-weight: 800;
        color: {BRAND_PRIMARY};
        margin-right: 10px;
      }}
      /* During active drag */
      li.sortable-chosen,
      li.sortable-ghost,
      li.sortable-drag {{
        background: #D9F0C2 !important;
        border-color: {BRAND_PRIMARY} !important;
        opacity: 0.95;
      }}

      /* Progress bar (solid) */
      .stProgress > div > div > div {{ background: {BRAND_PRIMARY} !important; }}
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
    defaults = {
        "page": 0,
        "answers": {},
        "submitted": False,
        "error_msg": "",
        # Brand ranking state (single list to rank all attributes)
        "brand_rank_order": None,  # list[str]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def navigate(delta: int):
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
                "<h1>IBA RadioPharma Solutions Quick Brand Perception survey</h1>",
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
        st.markdown('<h2 class="section-title">Tell us about you</h2>', unsafe_allow_html=True)
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
        cols = st.columns([1, 1], vertical_alignment="bottom")
        back_btn = cols[0].form_submit_button("Back")
        next_btn = cols[1].form_submit_button("Next")
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
        st.markdown('<h2 class="section-title">How familiar are you with the IBA brand?</h2>', unsafe_allow_html=True)
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
        cols = st.columns([1, 1], vertical_alignment="bottom")
        back_btn = cols[0].form_submit_button("Back")
        next_btn = cols[1].form_submit_button("Next")
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
            st.markdown('<h2 class="section-title">Where did you first hear about us?</h2>', unsafe_allow_html=True)
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

            st.markdown('<h2 class="section-title">Have you purchased any of the following solutions?</h2>', unsafe_allow_html=True)
            solutions = st.multiselect(
                "Select all that apply",
                [
                    "Cyclone® Key",
                    "Cyclone® Kiube",
                    "Cyclone® IKON",
                    "Cyclone® 30XP",
                    "Cyclone® 70",
                    "Cyclone® 18/9",
                    "Synthera®",
                    "Cassy®",
                    "Integralab®",
                ],
                key="solutions",
            )
            st.markdown('<hr class="divider" />', unsafe_allow_html=True)

            # Brand ranking — single sortable list (rank ALL attributes top→bottom)
            st.markdown('<h2 class="section-title">How would you describe the IBA brand?</h2>', unsafe_allow_html=True)
            st.caption("Drag to reorder: top = most representative, bottom = least.")

            default_attrs = [
                "Reliable",
                "Innovative",
                "Efficient",
                "Supportive",
                "Trusted Partner",
                "Flexible",
                "Expert-Led",
            ]
            if st.session_state.brand_rank_order is None:
                st.session_state.brand_rank_order = default_attrs

            dnd_ok = False
            try:
                from streamlit_sortables import sort_items  # pip install streamlit-sortables
                new_order = sort_items(
                    st.session_state.brand_rank_order,
                    direction="vertical",
                    key="brand_sort_single",
                )
                if isinstance(new_order, list) and len(new_order) == len(default_attrs):
                    st.session_state.brand_rank_order = new_order
                    dnd_ok = True
            except Exception:
                dnd_ok = False

            if not dnd_ok:
                # Fallback: show numbered select boxes to rank all items
                st.info("Drag-and-drop unavailable. Please rank all attributes from most to least.")
                remaining = default_attrs.copy()
                ranked: List[str] = []
                for i in range(len(default_attrs)):
                    choice = st.selectbox(f"Rank {i+1}", remaining, index=0, key=f"rank_all_{i}")
                    ranked.append(choice)
                    remaining.remove(choice)
                st.session_state.brand_rank_order = ranked

            st.markdown('<hr class="divider" />', unsafe_allow_html=True)
            cols = st.columns([1, 1], vertical_alignment="bottom")
            back_btn = cols[0].form_submit_button("Back")
            next_btn = cols[1].form_submit_button("Next")
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
                            "brand_attributes_ranked": st.session_state.brand_rank_order,
                        }
                    )
                    navigate(+1)

    else:
        with st.form("form_page_2_first", clear_on_submit=False):
            st.markdown('<h2 class="section-title">What problem are you trying to solve right now?</h2>', unsafe_allow_html=True)
            problem = st.text_input("Briefly describe (optional)", key="current_problem")
            st.markdown('<hr class="divider" />', unsafe_allow_html=True)
            cols = st.columns([1, 1], vertical_alignment="bottom")
            back_btn = cols[0].form_submit_button("Back")
            next_btn = cols[1].form_submit_button("Next")
            if back_btn:
                navigate(-1)
            if next_btn:
                st.session_state.answers.update({"current_problem": problem})
                navigate(+1)

# Page 3
elif st.session_state.page == 3:
    with st.form("form_page_3", clear_on_submit=False):
        st.markdown('<h2 class="section-title">Through which channels do you consume professional content?</h2>', unsafe_allow_html=True)
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

        st.markdown('<h2 class="section-title">Preferred content formats</h2>', unsafe_allow_html=True)
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

        st.markdown('<h2 class="section-title">Preferred video length</h2>', unsafe_allow_html=True)
        video_len = st.radio("", ["<60s", "1–3 min", "3–6 min", "6–12 min"], index=1, horizontal=True, key="video_length")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        cols = st.columns([1, 1], vertical_alignment="bottom")
        back_btn = cols[0].form_submit_button("Back")
        next_btn = cols[1].form_submit_button("Next")
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
        st.markdown('<h2 class="section-title">Which message resonates most?</h2>', unsafe_allow_html=True)

        message = st.radio(
            "Pick one",
            [
                "Empowering precision in nuclear medicine workflows—simplified, standardized, and scalable.",
                "From radiopharmaceutical preparation to clinical reporting—accelerated, reliable outcomes you can trust.",
                "Driving clinical impact through trusted radiopharma solutions—confidence at every step.",
            ],
            index=0,
            key="message_choice",
        )
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        st.markdown('<h2 class="section-title">How likely are you to recommend our content/products to a colleague?</h2>', unsafe_allow_html=True)
        nps = st.slider("", 0, 10, 8, key="likelihood_recommend")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        st.markdown('<h2 class="section-title">One thing we could do to be more valuable to you (optional)</h2>', unsafe_allow_html=True)
        one_thing = st.text_area("", height=80, key="improve_one_thing")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        cols = st.columns([1, 1], vertical_alignment="bottom")
        back_btn = cols[0].form_submit_button("Back")
        next_btn = cols[1].form_submit_button("Next")
        if back_btn:
            navigate(-1)
        if next_btn:
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
        st.markdown('<h2 class="section-title">Stay in touch</h2>', unsafe_allow_html=True)
        st.write("By submitting this form you consent to the processing of your responses for research and personalization purposes.")
        email = st.text_input("Work email (optional)", key="email")
        do_not_contact = st.checkbox("I don't want to receive relevant content updates in the future", value=False, key="do_not_contact")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        staff = st.text_input(
            "Staff initials (optional)",
            value=st.session_state.answers.get("staff_initials", ""),
            key="staff_initials_input",
        )

        cols = st.columns([1, 1], vertical_alignment="bottom")
        back_btn = cols[0].form_submit_button("Back")
        submit_btn = cols[1].form_submit_button("Submit")
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
