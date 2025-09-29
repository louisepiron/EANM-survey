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

      /* H1 form title bar (solid green), H1 text inside (slightly smaller) */
      .brand-header {{
        background: {BRAND_PRIMARY};
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: white;
      }}
      .brand-header h1 {{
        font-weight: 850;
        font-size: 2.0rem;     /* H1 slightly smaller */
        margin: 0;
        line-height: 1.1;
      }}

      /* H2 section/question titles */
      h2.section-title {{
        font-weight: 750;
        font-size: 1.45rem;    /* H2 */
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

      /* Buttons — force solid green */
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

      /* Answer zones: light gray by default; green on focus/active */

      /* Select/Multiselect (BaseWeb Select) */
      div[data-baseweb="select"] > div {{
        border: 2px solid {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        transition: border-color 120ms ease-in-out;
      }}
      div[data-baseweb="select"]:focus-within > div,
      div[data-baseweb="select"][aria-expanded="true"] > div {{
        border-color: {BRAND_PRIMARY} !important;
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

      /* SortableJS containers (Pool + Boxes 1..5) */
      /* Make containers (the drop zones) white with light grey border */
      ul.sortable, .sortable, .sortable-container {{
        background: #FFFFFF !important;
        border: 2px dashed {DIVIDER_COLOR} !important;
        border-radius: 10px !important;
        min-height: 52px; /* so empty boxes are clearly visible */
        padding: 8px !important;
        margin-bottom: 10px !important;
        list-style: none !important;
      }}

      /* Sortable items (attributes) with green styling */
      ul.sortable li,
      .sortable li,
      li.sortable-item {{
        background: #E8F6DC !important;                 /* green-tinted */
        border: 2px solid {BRAND_PRIMARY} !important;   /* green border */
        border-radius: 10px !important;
        padding: 10px 12px !important;
        margin-bottom: 8px !important;
        list-style: none !important;
      }}
      /* During active drag */
      li.sortable-chosen,
      li.sortable-ghost,
      li.sortable-drag {{
        background: #D9F0C2 !important;
        border-color: {BRAND_PRIMARY} !important;
        opacity: 0.95;
      }}

      /* Labels row under the Pool to indicate boxes 1..5 */
      .rank-labels {{
        display: grid;
        grid-template-columns: 1fr;
        row-gap: 10px;
        margin: 6px 0 8px 0;
      }}
      .rank-label {{
        font-weight: 700;
        font-size: 0.95rem;
        color: #4a4a4a;
        margin: 0 0 4px 0;
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
        # Brand ranking state
        "brand_pool": None,            # list[str]
        "brand_rank_1": [],
        "brand_rank_2": [],
        "brand_rank_3": [],
        "brand_rank_4": [],
        "brand_rank_5": [],
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

            # Brand ranking with Pool + 5 true connected drop-boxes (1..5)
            st.markdown('<h2 class="section-title">How would you describe the IBA brand?</h2>', unsafe_allow_html=True)
            st.caption("Drag attributes from the Pool into the boxes 1 (most representative) to 5 (least).")

            default_attrs = [
                "Reliable",
                "Innovative",
                "Efficient",
                "Supportive",
                "Trusted Partner",
                "Flexible",
                "Expert-Led",
            ]

            # Initialize lists
            if st.session_state.brand_pool is None:
                st.session_state.brand_pool = default_attrs.copy()
                st.session_state.brand_rank_1 = []
                st.session_state.brand_rank_2 = []
                st.session_state.brand_rank_3 = []
                st.session_state.brand_rank_4 = []
                st.session_state.brand_rank_5 = []

            # Render Pool label
            st.markdown("Pool")
            dnd_ok = False
            try:
                from streamlit_sortables import sort_items  # pip install streamlit-sortables

                # Items structure: [Pool, 1, 2, 3, 4, 5]
                items = [
                    st.session_state.brand_pool,
                    st.session_state.brand_rank_1,
                    st.session_state.brand_rank_2,
                    st.session_state.brand_rank_3,
                    st.session_state.brand_rank_4,
                    st.session_state.brand_rank_5,
                ]

                # Render the connected lists (vertical stack)
                new_lists = sort_items(
                    items,
                    multi_containers=True,
                    direction="vertical",
                    key="brand_sort_multi",
                )

                if isinstance(new_lists, list) and len(new_lists) == 6:
                    st.session_state.brand_pool = new_lists[0]
                    st.session_state.brand_rank_1 = new_lists[1]
                    st.session_state.brand_rank_2 = new_lists[2]
                    st.session_state.brand_rank_3 = new_lists[3]
                    st.session_state.brand_rank_4 = new_lists[4]
                    st.session_state.brand_rank_5 = new_lists[5]
                    dnd_ok = True

                # Show numeric labels under Pool to make it obvious these are the target boxes
                st.markdown(
                    '<div class="rank-labels">'
                    '<div class="rank-label">1</div>'
                    '<div class="rank-label">2</div>'
                    '<div class="rank-label">3</div>'
                    '<div class="rank-label">4</div>'
                    '<div class="rank-label">5</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )

            except Exception:
                dnd_ok = False

            if not dnd_ok:
                # Fallback: 5 pickers ensuring uniqueness
                st.info("Drag-and-drop unavailable. Please pick your top 5 attributes in order.")
                remaining = default_attrs.copy()
                r1 = st.selectbox("Rank 1 (most representative)", remaining, index=0, key="rank_sel_1")
                remaining.remove(r1)
                r2 = st.selectbox("Rank 2", remaining, index=0, key="rank_sel_2")
                remaining.remove(r2)
                r3 = st.selectbox("Rank 3", remaining, index=0, key="rank_sel_3")
                remaining.remove(r3)
                r4 = st.selectbox("Rank 4", remaining, index=0, key="rank_sel_4")
                remaining.remove(r4)
                r5 = st.selectbox("Rank 5 (least of the five)", remaining, index=0, key="rank_sel_5")

                st.session_state.brand_rank_1 = [r1]
                st.session_state.brand_rank_2 = [r2]
                st.session_state.brand_rank_3 = [r3]
                st.session_state.brand_rank_4 = [r4]
                st.session_state.brand_rank_5 = [r5]
                st.session_state.brand_pool = remaining

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
                    ranks = [
                        st.session_state.brand_rank_1,
                        st.session_state.brand_rank_2,
                        st.session_state.brand_rank_3,
                        st.session_state.brand_rank_4,
                        st.session_state.brand_rank_5,
                    ]
                    if not all(len(r) == 1 for r in ranks):
                        st.toast("Please place exactly one attribute in each box 1–5.", icon="⚠️")
                    else:
                        ranked = [r[0] for r in ranks]
                        st.session_state.answers.update(
                            {
                                "first_touch": first_touch,
                                "solutions": solutions,
                                "brand_attributes_ranked": ranked,
                            }
                        )
                        navigate(+1)

    else:
        with st.form("form_page_2_first", clear_on_submit=False):
            st.markdown('<h2 class="section-title">What problem are you trying to solve right now?</h2>', unsafe_allow_html=True)
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
        st.markdown('<h2 class="section-title">Which message resonates most?</h2>', unsafe_allow_html=True)
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

        st.markdown('<h2 class="section-title">How likely are you to recommend our content/products to a colleague?</h2>', unsafe_allow_html=True)
        nps = st.slider("", 0, 10, 8, key="likelihood_recommend")
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)

        st.markdown('<h2 class="section-title">One thing we could do to be more valuable to you (optional)</h2>', unsafe_allow_html=True)
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
