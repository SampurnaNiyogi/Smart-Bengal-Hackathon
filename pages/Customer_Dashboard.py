import streamlit as st
import requests


# Custom Sidebar Styling
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(145deg, #1f1f2f, #191926);
            padding-top: 2rem;
            transition: all 0.3s ease-in-out;
        }
        [data-testid="stSidebar"]:hover {
            background: linear-gradient(145deg, #292940, #1f1f2f);
        }
        [data-testid="stSidebar"] * {
            color: #f0f0f0 !important;
            font-family: 'Segoe UI', sans-serif;
        }
        .stSelectbox > div {
            padding: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    page = st.selectbox("📂 Navigate to", [
        "🏠 Main",
        "🛒 Cart Dashboard",
        "👥 Customer Dashboard",
        "🔐 Login",
        "💳 Payment Page",
        "🔎 Search Dashboard",
        "🗺️ Store Map"
    ])

# Route (manual redirect if all logic is in main.py)
if page == "🏠 Main":
    st.title("")
elif page == "🛒 Cart Dashboard":
    st.switch_page("pages/Cart_Dashboard.py")
elif page == "👥 Customer Dashboard":
    st.switch_page("pages/Customer_Dashboard.py")
elif page == "🔐 Login":
    st.switch_page("pages/Login.py")
elif page == "💳 Payment Page":
    st.switch_page("pages/Payment_page.py")
elif page == "🔎 Search Dashboard":
    st.switch_page("pages/Search_Dashboard.py")
elif page == "🗺️ Store Map":
    st.switch_page("pages/Store_map.py")

# Hide default Streamlit sidebar & footer
st.markdown("""
    <style>
        /* Hide top-right hamburger menu */
        #MainMenu {visibility: hidden;}
        
        /* Hide footer */
        footer {visibility: hidden;}
        
        /* Optional: Hide sidebar toggle completely */
        .css-1d391kg {display: none}
    </style>
""", unsafe_allow_html=True)





# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #F2EFE7;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #3498db, #006A71);
        color: white;
        padding: 1rem;
        border-radius: 10px;
    }
    
    .welcome-message {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 2rem;
        color: #7AC6D2
    }
    
    .selection-container {
        background-color: transparent;
        padding: 1.5rem;
        border-radius: 0px;
        box-shadow: 0 0px 0px rgba(0, 0, 0, 0);
        margin-bottom: 2rem;
        height: 0px
    }
    
    .selection-header {
        font-size: 0rem;
        font-weight: 0;
        margin-bottom: 0;
        color: #2c3e50;
    }
    
    .selection-result {
        background-color: transparent;
        padding: 0.8rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        border-left: 4px solid #3498db;
    }
    
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .stButton>button {
        background-color: #3674B5;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 500;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
        color: #E8C999 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .cart-button button {
        background-color: #27ae60 !important;
    }
    
    .cart-button button:hover {
        background-color: #219653 !important;
        color: #D1F8EF
    }
    
    .st-selectbox {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:5000"

if "user_name" in st.session_state:
    name = st.session_state['user_name']

if "retail" not in st.session_state:
    st.session_state.retail = False

if "branch" not in st.session_state:
    st.session_state.branch = False

# Main header
st.markdown(f'<div class="main-header">Smart Cashier-less Retail System</div>', unsafe_allow_html=True)
st.markdown(f'<div class="welcome-message">Hi {name}! Welcome to our smart shopping experience.</div>',
            unsafe_allow_html=True)

# Fetch retailers
response = requests.get(f"{BASE_URL}/get_providers")
if response.status_code == 200:
    provider_options = response.json()  # List of provider document names
else:
    provider_options = ["Error fetching retail"]

# Retailer selection section
# st.markdown('<div class="selection-container">', unsafe_allow_html=True)
st.markdown('<div class="selection-header">Select Your Retailer</div>', unsafe_allow_html=True)

retailer_option = st.selectbox("Select retailer:", provider_options)
st.session_state.retail = retailer_option

# Fetch branches dynamically based on selected provider
if retailer_option and retailer_option != "Error fetching providers":

    # st.markdown(f'<div class="selection-result">Selected retailer: {retailer_option}</div>', unsafe_allow_html=True)
    # Fetch branches dynamically based on selected provider
    response_branches = requests.get(f"{BASE_URL}/{retailer_option}/get_branch")

    if response_branches.status_code == 200:
        branch_options = response_branches.json()
    else:
        branch_options = ["No branches found"]

    st.markdown('<div class="selection-header" style="margin-top: 1rem;">Select Branch Location</div>',
                unsafe_allow_html=True)
    selected_branch = st.selectbox("Choose a Branch:", branch_options, label_visibility="collapsed")
    st.session_state.branch = selected_branch

    # if selected_branch:
    # st.markdown(f'<div class="selection-result">Selected branch: {selected_branch}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Action buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Search Products"):
        st.switch_page("pages/Search_dashboard.py")

with col2:
    if st.button("🛒 View Cart"):
        st.switch_page("pages/Cart_dashboard.py")
    st.markdown('</div>', unsafe_allow_html=True)
