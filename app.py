import os
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st

from utils.g_sheets import append_to_google_sheet

# ----------------------------
# Constants and Configuration
# ----------------------------
BRAND_PRIMARY = "#69BE28"   # Green
BRAND_NEUTRAL = "#808691"   # Neutral gray for accents
DIVIDER_COLOR = "#E6E8EB"   # Light grey divider
FONT_STACK = "'Simplon Norm', Arial, sans-serif"
LOGO_PATH = "assets/logo.png"

PAGE_TITLE = "IBA RadioPharma Solutions Quick Brand Perception survey"
TOTAL_PAGES = 6

# Form options
ROLE_OPTIONS = ["", "Physician", "Medical Physicist", "Researcher", "Industry", "Radiopharmacist", "Other"]
REGION_OPTIONS = ["", "EU", "North America", "LATAM", "APAC", "Middle East", "Africa"]
FAMILIARITY_OPTIONS = [
    "I'm a current customer",
    "I've been a customer",
    "I'm not a customer but I'm considering purchasing a product",
    "I'm familiar with IBA but don't have / plan to buy a product",
    "It's the first time I hear about IBA",
]
TOUCHPOINT_OPTIONS = [
    "", "Colleague / Friend", "Congress", "IBA website", "Search (Google)",
    "Email newsletter", "LinkedIn", "Instagram", "Other",
]
SOLUTION_OPTIONS = [
    "Cyclone® Key", "Cyclone® Kiube", "Cyclone® IKON", "Cyclone® 30XP",
    "Cyclone® 70", "Cyclone® 18/9", "Synthera®", "Cassy®", "Integralab®",
]
BRAND_ATTRIBUTES = [
    "Reliable", "Innovative", "Efficient", "Supportive",
    "Trusted Partner", "Flexible", "Expert-Led",
]
CHANNEL_OPTIONS = [
    "LinkedIn", "Instagram", "YouTube", "Industry association websites",
    "Email newsletters", "Webinars", "Podcasts", "X/Twitter",
    "ResearchGate", "Google", "Other",
]
FORMAT_OPTIONS = [
    "Short video (<2 min) quick tips", "Video demos (3–6 min)", "Case studies",
    "Protocols / how-tos (step-by-step guides)", "Webinars (live or on-demand)",
    "White papers / technical briefs", "Email digest / newsletter", "Podcasts",
]
VIDEO_LENGTH_OPTIONS = ["<60s", "1–3 min", "3–6 min", "6–12 min"]
MESSAGE_OPTIONS = [
    "Empowering precision in nuclear medicine workflows—simplified, standardized, and scalable.",
    "From radiopharmaceutical preparation to clinical reporting—accelerated, reliable outcomes you can trust.",
    "Driving clinical impact through trusted radiopharma solutions—confidence at every step.",
]

# ----------------------------
# App Configuration
# ----------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Styles
# ----------------------------
def apply_custom_styles():
    """Apply all custom CSS styles"""
    st.markdown(
        f"""
        <style>
          /* Base font and colors */
          html, body, [class*="css"] {{
            font-family: {FONT_STACK} !important;
            color: #1c1c1c;
          }}

          /* Hide Streamlit branding and UI elements */
          [data-testid="stToolbar"],
          [data-testid="stDecoration"],
          [data-testid="viewerBadge"],
          [data-testid="stStatusWidget"],
          [data-testid="stHeaderActionMenu"],
          header, #MainMenu, footer {{
            display: none !important;
          }}

          /* Hide GitHub/external branding */
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

          /* Mobile GitHub branding removal */
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
            [data-testid*="badge"] {{
              display: none !important;
            }}
          }}

          /* Layout adjustments */
          .block-container {{
            padding-top: 0.5rem;
            padding-bottom: 1rem;
          }}

          /* Brand header styling */
          .brand-header {{
            background: {BRAND_PRIMARY};
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 10px;
            color: white;
          }}
          
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

          /* Section titles */
          h2.section-title {{
            font-weight: 750;
            font-size: 1.45rem;
            margin: 0 0 0.5rem 0;
            color: #1c1c1c;
          }}

          /* Utility classes */
          .subtle {{ color: {BRAND_NEUTRAL}; }}
          hr.divider {{
            border: none;
            border-top: 1px solid {DIVIDER_COLOR};
            margin: 10px 0 14px 0;
          }}

          /* Button styling */
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
          [data-testid="baseButton-primary"]:hover {{
            filter: brightness(0.98);
          }}
          
          .stButton > button:disabled,
          .stForm .stButton > button:disabled {{
            opacity: 0.6 !important;
          }}

          /* Button layout - two column grid */
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

          /* Form input styling */
          div[data-baseweb="select"] > div {{
            border: 2px solid {DIVIDER_COLOR} !important;
            border-radius: 10px !important;
            transition: border-color 120ms ease-in-out;
          }}
          
          div[data-baseweb="select"]:focus-within > div,
          div[data-baseweb="select"][aria-expanded="true"] > div {{
            border-color: {BRAND_PRIMARY} !important;
          }}

          .stTextInput > div > div,
          .stTextArea > div > div {{
            border: 2px solid {DIVIDER_COLOR} !important;
            border-radius: 10px !important;
            padding: 2px 8px !important;
            transition: border-color 120ms ease-in-out;
          }}
          
          .stTextInput > div > div:focus-within,
          .stTextArea > div > div:focus-within {{
            border-color: {BRAND_PRIMARY} !important;
          }}

          .stRadio > div {{
            border: 2px solid {DIVIDER_COLOR} !important;
            border-radius: 10px !important;
            padding: 6px 10px !important;
            transition: border-color 120ms ease-in-out;
          }}
          
          .stRadio > div:focus-within {{
            border-color: {BRAND_PRIMARY} !important;
          }}
          
          .stRadio label {{
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            line-height: 1.3 !important;
          }}

          /* Sortable list styling */
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
            background: #E8F6DC !important;
            border: 2px solid {BRAND_PRIMARY} !important;
            border-radius: 10px !important;
            padding: 10px 12px !important;
            margin-bottom: 8px !important;
            list-style: none !important;
            display: flex;
            align-items: center;
          }}
          
          ul.sortable li::before {{
            counter-increment: rank;
            content: counter(rank) ".";
            font-weight: 800;
            color: {BRAND_PRIMARY};
            margin-right: 10px;
          }}
          
          li.sortable-chosen,
          li.sortable-ghost,
          li.sortable-drag {{
            background: #D9F0C2 !important;
            border-color: {BRAND_PRIMARY} !important;
            opacity: 0.95;
          }}

          /* Progress bar */
          .stProgress > div > div > div {{
            background: {BRAND_PRIMARY} !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------
# Utility Functions
# ----------------------------
def get_query_param(name: str, default: str = "") -> str:
    """Get query parameter with fallback for older Streamlit versions"""
    try:
        return st.query_params.get(name, default)
    except Exception:
        qp = st.experimental_get_query_params()
        return qp.get(name, [default])[0] if qp else default

def init_session_state():
    """Initialize session state with default values"""
    defaults = {
        "page": 0,
        "answers": {},
        "submitted": False,
        "error_msg": "",
        "brand_rank_order": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def navigate(delta: int):
    """Navigate between pages"""
    st.session_state.page = max(0, st.session_state.page + delta)
    st.session_state["_nav_event_at"] = datetime.utcnow().isoformat()
    st.rerun()

def render_header():
    """Render the branded header with logo and title"""
    with st.container():
        st.markdown('<div class="brand-header">', unsafe_allow_html=True)
        col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
        
        with col_logo:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=64)
        
        with col_title:
            st.markdown(f"<h1>{PAGE_TITLE}</h1>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def validate_required_fields(fields: Dict[str, Any]) -> List[str]:
    """Validate required fields and return list of missing ones"""
    missing = []
    for key, value in fields.items():
        if value is None:
            missing.append(key)
        elif isinstance(value, str) and value.strip() == "":
            missing.append(key)
        elif isinstance(value, list) and len(value) == 0:
            missing.append(key)
    return missing

def render_navigation_buttons(back_enabled: bool = True):
    """Render standard back/next navigation buttons"""
    st.markdown('<hr class="divider" />', unsafe_allow_html=True)
    cols = st.columns([1, 1], vertical_alignment="bottom")
    
    back_btn = cols[0].form_submit_button("Back") if back_enabled else None
    next_btn = cols[1].form_submit_button("Next")
    
    return back_btn, next_btn

def render_section_title(title: str):
    """Render a section title with consistent styling"""
    st.markdown(f'<h2 class="section-title">{title}</h2>', unsafe_allow_html=True)

def handle_brand_ranking():
    """Handle brand attribute ranking with drag-and-drop or fallback"""
    if st.session_state.brand_rank_order is None:
        st.session_state.brand_rank_order = BRAND_ATTRIBUTES.copy()

    try:
        from streamlit_sortables import sort_items
        new_order = sort_items(
            st.session_state.brand_rank_order,
            direction="vertical",
            key="brand_sort_single",
        )
        if isinstance(new_order, list) and len(new_order) == len(BRAND_ATTRIBUTES):
            st.session_state.brand_rank_order = new_order
            return True
    except ImportError:
        pass
    
    # Fallback: numbered select boxes
    st.info("Drag-and-drop unavailable. Please rank all attributes from most to least.")
    remaining = BRAND_ATTRIBUTES.copy()
    ranked = []
    
    for i in range(len(BRAND_ATTRIBUTES)):
        choice = st.selectbox(f"Rank {i+1}", remaining, index=0, key=f"rank_all_{i}")
        ranked.append(choice)
        remaining.remove(choice)
    
    st.session_state.brand_rank_order = ranked
    return False

def submit_survey_data():
    """Submit survey data to Google Sheets"""
    answers = st.session_state.answers.copy()
    answers.update({
        "consent": True,
        "email": st.session_state.get("email", "").strip(),
        "do_not_contact": st.session_state.get("do_not_contact", False),
        "staff_initials": st.session_state.get("staff_initials_input", "").strip(),
        "timestamp_utc": datetime.utcnow().isoformat(),
    })
    
    # Convert lists to comma-separated strings
    for key in ["channels", "formats", "solutions", "brand_attributes_ranked"]:
        if key in answers and isinstance(answers[key], list):
            answers[key] = ", ".join(answers[key])
    
    try:
        append_to_google_sheet(answers)
        st.session_state.submitted = True
        navigate(+1)
    except Exception as e:
        st.error(f"Submission failed: {e}")
        st.info("Please check your internet connection and try again.")

# ----------------------------
# Page Renderers
# ----------------------------
def render_page_0():
    """Page 0: Demographics"""
    with st.form("form_page_0", clear_on_submit=False):
        render_section_title("Tell us about you")
        
        role = st.selectbox("Role", ROLE_OPTIONS, index=0, key="role")
        region = st.selectbox("Region", REGION_OPTIONS, index=0, key="region")
        
        back_btn, next_btn = render_navigation_buttons(back_enabled=False)
        
        if next_btn:
            missing = validate_required_fields({"Role": role, "Region": region})
            if missing:
                st.toast("Please select your Role and Region.", icon="⚠️")
            else:
                st.session_state.answers.update({"role": role, "region": region})
                navigate(+1)

def render_page_1():
    """Page 1: Brand familiarity"""
    with st.form("form_page_1", clear_on_submit=False):
        render_section_title("How familiar are you with the IBA brand?")
        
        familiarity = st.selectbox("Select one", FAMILIARITY_OPTIONS, index=2, key="familiarity")
        
        back_btn, next_btn = render_navigation_buttons()
        
        if back_btn:
            navigate(-1)
        if next_btn:
            st.session_state.answers["familiarity"] = familiarity
            navigate(+1)

def render_page_2():
    """Page 2: Brand touchpoints and attributes (conditional)"""
    familiarity = st.session_state.answers.get("familiarity", "")
    is_first_time = familiarity == "It's the first time I hear about IBA"

    if not is_first_time:
        render_page_2_existing_users()
    else:
        render_page_2_first_time_users()

def render_page_2_existing_users():
    """Page 2 for existing users: touchpoints, solutions, brand attributes"""
    with st.form("form_page_2_known", clear_on_submit=False):
        render_section_title("Where did you first hear about us?")
        first_touch = st.selectbox("Choose one", TOUCHPOINT_OPTIONS, index=0, key="first_touch")
        
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        
        render_section_title("Have you purchased any of the following solutions?")
        solutions = st.multiselect("Select all that apply", SOLUTION_OPTIONS, key="solutions")
        
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        
        render_section_title("How would you describe the IBA brand?")
        st.caption("Drag to reorder: top = most representative, bottom = least.")
        
        handle_brand_ranking()
        
        back_btn, next_btn = render_navigation_buttons()
        
        if back_btn:
            navigate(-1)
        if next_btn:
            missing = validate_required_fields({"First touchpoint": first_touch})
            if missing:
                st.toast("Please complete the required fields.", icon="⚠️")
            else:
                st.session_state.answers.update({
                    "first_touch": first_touch,
                    "solutions": solutions,
                    "brand_attributes_ranked": st.session_state.brand_rank_order,
                })
                navigate(+1)

def render_page_2_first_time_users():
    """Page 2 for first-time users: current problem"""
    with st.form("form_page_2_first", clear_on_submit=False):
        render_section_title("What problem are you trying to solve right now?")
        problem = st.text_input("Briefly describe (optional)", key="current_problem")
        
        back_btn, next_btn = render_navigation_buttons()
        
        if back_btn:
            navigate(-1)
        if next_btn:
            st.session_state.answers.update({"current_problem": problem})
            navigate(+1)

def render_page_3():
    """Page 3: Content consumption preferences"""
    with st.form("form_page_3", clear_on_submit=False):
        render_section_title("Through which channels do you consume professional content?")
        channels = st.multiselect("Select all that apply", CHANNEL_OPTIONS, key="channels")
        
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        
        render_section_title("Preferred content formats")
        formats = st.multiselect("Select all that apply", FORMAT_OPTIONS, key="formats")
        
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        
        render_section_title("Preferred video length")
        video_length = st.radio("", VIDEO_LENGTH_OPTIONS, index=1, horizontal=True, key="video_length")
        
        back_btn, next_btn = render_navigation_buttons()
        
        if back_btn:
            navigate(-1)
        if next_btn:
            missing = validate_required_fields({
                "Channels": channels,
                "Formats": formats,
                "Video length": video_length
            })
            if missing:
                st.toast("Please select at least one channel and format.", icon="⚠️")
            else:
                st.session_state.answers.update({
                    "channels": channels,
                    "formats": formats,
                    "video_length": video_length,
                })
                navigate(+1)

def render_page_4():
    """Page 4: Message resonance and feedback"""
    with st.form("form_page_4", clear_on_submit=False):
        render_section_title("Which message resonates most?")
        message_choice = st.radio("Pick one", MESSAGE_OPTIONS, index=0, key="message_choice")
        
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        
        render_section_title("How likely are you to recommend our content/products to a colleague?")
        likelihood_recommend = st.slider("", 0, 10, 8, key="likelihood_recommend")
        
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        
        render_section_title("One thing we could do to be more valuable to you (optional)")
        improve_one_thing = st.text_area("", height=80, key="improve_one_thing")
        
        back_btn, next_btn = render_navigation_buttons()
        
        if back_btn:
            navigate(-1)
        if next_btn:
            st.session_state.answers.update({
                "message_choice": message_choice,
                "likelihood_recommend": likelihood_recommend,
                "improve_one_thing": improve_one_thing,
            })
            navigate(+1)

def render_page_5():
    """Page 5: Contact information and submission"""
    with st.form("form_page_5", clear_on_submit=False):
        render_section_title("Stay in touch")
        st.write("By submitting this form you consent to the processing of your responses for research and personalization purposes.")
        
        email = st.text_input("Work email (optional)", key="email")
        do_not_contact = st.checkbox(
            "I don't want to receive relevant content updates in the future",
            value=False,
            key="do_not_contact"
        )
        
        st.markdown('<hr class="divider" />', unsafe_allow_html=True)
        
        staff_initials = st.text_input(
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
            submit_survey_data()

def render_thank_you_page():
    """Thank you page"""
    st.success("Thank you! Your responses have been recorded.")
    
    def reset_survey():
        st.session_state.update({
            "page": 0,
            "answers": {},
            "submitted": False,
            "error_msg": "",
            "brand_rank_order": None,
        })
        st.rerun()
    
    st.button("Start another response ↺", on_click=reset_survey)

# ----------------------------
# Main Application
# ----------------------------
def main():
    """Main application function"""
    # Initialize
    init_session_state()
    apply_custom_styles()
    render_header()
    
    # Handle staff initials from URL
    staff_initials = get_query_param("staff", "")
    if staff_initials:
        st.session_state.answers["staff_initials"] = staff_initials
    
    # Progress bar
    progress = min(st.session_state.page / TOTAL_PAGES, 1.0)
    st.progress(progress)
    
    # Route to appropriate page
    page_renderers = {
        0: render_page_0,
        1: render_page_1,
        2: render_page_2,
        3: render_page_3,
        4: render_page_4,
        5: render_page_5,
    }
    
    current_page = st.session_state.page
    if current_page in page_renderers:
        page_renderers[current_page]()
    else:
        render_thank_you_page()

if __name__ == "__main__":
    main()
