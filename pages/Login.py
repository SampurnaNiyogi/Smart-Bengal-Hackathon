import re
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time
from dotenv import load_dotenv
import os
from PIL import Image
import base64
import uuid
import random

# Set page config early
st.set_page_config(page_title="Smart Retail - Login", page_icon="🛒", layout="centered")

# Load environment variables from .env
load_dotenv()
service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not service_account_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set in the .env file")

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

if "user_registered" not in st.session_state:
    st.session_state.user_registered = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "fingerprint" not in st.session_state:
    st.session_state.fingerprint = False

if "fingerprint_scan_progress" not in st.session_state:
    st.session_state.fingerprint_scan_progress = 0

# Convert image to base64 string
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded}"


# Apply custom CSS
def apply_custom_css():
    # Shopping Cart SVG Animation
    loading_svg = """
    <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g>
                <circle cx="9" cy="20" r="1.5" fill="#3498db">
                    <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
                </circle>
                <circle cx="17" cy="20" r="1.5" fill="#3498db">
                    <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
                </circle>
                <path d="M4 4H6L9 15H17L20 8H8" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <animateTransform attributeName="transform" type="translate" values="0 0; 1 -1; 0 0" dur="0.6s" repeatCount="indefinite"/>
                </path>
            </g>
        </svg>
    </div>
    """
    st.markdown("""
    <style>
        :root {
            --primary-color: #3498db;
            --secondary-color: #2ecc71;
            --accent-color: #f39c12;
            --background-color: #f5f7fa;
            --text-color: #2c3e50;
            --card-bg: #ffffff;
            --error-color: #e74c3c;
            --success-color: #27ae60;
        }

        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 12px 20px;
            font-weight: 500;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stTextInput > div > div > input {
            border-radius: 8px;
            padding: 12px 15px;
            border: 1px solid #dfe6e9;
            font-size: 16px;
        }
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: none;
        }
        .logo-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo-icon {
            font-size: 50px;
            color: var(--primary-color);
        }
        h1, h2, h3 {
            color: var(--primary-color);
        }
        .subtitle {
            color: #7f8c8d;
            font-size: 16px;
        }
        .divider {
            display: flex;
            align-items: center;
            margin: 20px 0;
            color: #7f8c8d;
        }
        .divider::before, .divider::after {
            content: "";
            flex: 1;
            border-bottom: 1px solid #dfe6e9;
        }
        .divider span {
            padding: 0 10px;
            font-size: 14px;
        }
        .fingerprint-button {
            border: none;
            background: none;
            padding: 0;
            cursor: pointer;
            display: flex;
            justify-content: center;
        }
        .fingerprint-img {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            transition: transform 0.3s ease;
            cursor: pointer;
        }
        .fingerprint-img:hover {
            transform: scale(1.05);
        }
        .centered-text {
            text-align: center;
            font-size: 1.2rem;
            margin-top: 1rem;
            color: #333;
        }
        
        /* Fingerprint scan animation */
        .scan-line {
            height: 5px;
            background: linear-gradient(to right, transparent, #3498db, transparent);
            position: absolute;
            width: 100%;
            animation: scan 2s ease-in-out infinite;
        }
        @keyframes scan {
            0% { top: 0; }
            50% { top: 100%; }
            100% { top: 0; }
        }
        .fingerprint-container {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto;
            border-radius: 10px;
            overflow: hidden;
        }
        .fingerprint-scan {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
    </style>
    """, unsafe_allow_html=True)

def login_page():
    apply_custom_css()
     # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom container for login options
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Welcome</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Sign in or create an account to continue</p>', unsafe_allow_html=True)
    
    # Create two columns for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Sign In"):
            st.session_state.user_registered = "Existing"
            st.rerun()
    
    with col2:
        if st.button("Sign Up"):
            st.session_state.user_registered = "New User"
            st.rerun()
    
    # Divider and biometric options
    st.markdown("""<div class="divider"><span>or continue with</span></div>""", unsafe_allow_html=True)
    
    fingerprint_base64 = get_base64_encoded_image("assets/fingerprint.jpg")
    
    # Make the fingerprint image clickable
    col = st.columns([1, 2, 1])[1]  # Centered column
    with col:
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <img src='{fingerprint_base64}' width='100' id="fingerprint-img" 
                style='cursor: pointer;' onclick="
                    element = window.parent.document.getElementById('fingerprint-button');
                    element.click();
                "/>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Hidden button that will be triggered by the image click
        if st.button("", key="fingerprint-button", help="Use fingerprint to log in"):
            st.session_state.fingerprint = True
            st.rerun()

    st.markdown("<p style='text-align: center; color: #7f8c8d; margin-top: 10px;'>Tap to use fingerprint</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def validate_name_email(name: str, email: str) -> bool:
    if not name and not email:
        st.error("Both name and email fields are empty")
        return False
    elif not name:
        st.error("Name field is empty")
        return False
    elif not email:
        st.error("Email field is empty")
        return False
    # Cryptic email regex for email validation
    email_regex = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")
    if not email_regex.match(email):
        st.error("Email address is not valid")
        return False
    return True

def add_user(name, email):
    try:
        is_valid = validate_name_email(name, email)
        if not is_valid:
            return False
        users_ref = db.collection("users").document(name)
        fingerprint_id = str(uuid.uuid4())[:8]  # Generate short unique ID
        users_ref.set({
            "name": name,
            "email": email,
            "fingerprint_id": fingerprint_id
        })
        st.session_state.user_registered = True
        return True
    except Exception as e:
        st.error(f"Error adding user: {e}")
        return False

def register():
    apply_custom_css()
    
    # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom container for sign up form
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Create Account</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Join our smart shopping experience</p>', unsafe_allow_html=True)
    
    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")
    
    if st.button("Sign Up"):
        if add_user(name, email):
            st.success(f"User {name} added successfully!")
            st.session_state.page = "consumer_dashboard"
            st.session_state.user_registered = "Existing"
            status_placeholder = st.empty()
            with status_placeholder.status("Loading......"):
                for i in range(2):
                    time.sleep(1)
            time.sleep(2)
            status_placeholder.empty()
            st.rerun()
    # Back button
    if st.button("Back to Login"):
        st.session_state.user_registered = "None"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def authenticate() -> None:
    apply_custom_css()
     # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom container for sign in form
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Sign In</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Enter your details to continue</p>', unsafe_allow_html=True)

    u_name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")

    if st.button("Sign In"):
        is_valid = validate_name_email(u_name, email)
        if not is_valid:
            return
        user_ref = db.collection("users").where("name", "==", u_name).where("email", "==", email).get()

        if user_ref:
            st.session_state["user_name"] = u_name
            # Centered Loading Text
            status_text = st.empty()
            status_text.markdown("<h3 style='text-align: center;'>Entering Store.....</h3>", unsafe_allow_html=True)

            # Shopping Cart SVG Animation
            loading_svg = """
            <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <g>
                        <circle cx="9" cy="20" r="1.5" fill="#3498db">
                            <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
                        </circle>
                        <circle cx="17" cy="20" r="1.5" fill="#3498db">
                            <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
                        </circle>
                        <path d="M4 4H6L9 15H17L20 8H8" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <animateTransform attributeName="transform" type="translate" values="0 0; 1 -1; 0 0" dur="0.6s" repeatCount="indefinite"/>
                        </path>
                    </g>
                </svg>
            </div>
            """

            loading_placeholder = st.empty()
            loading_placeholder.markdown(loading_svg, unsafe_allow_html=True)
            time.sleep(2)
            st.switch_page("pages/Customer_dashboard.py")
        else:
            st.error("Incorrect name or email")
    # Back button
    if st.button("Back to Login"):
        st.session_state.user_registered = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def fingerprint_auth():
    apply_custom_css()
    # Shopping Cart SVG Animation
    loading_svg = """
    <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g>
                <circle cx="9" cy="20" r="1.5" fill="#3498db">
                    <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
                </circle>
                <circle cx="17" cy="20" r="1.5" fill="#3498db">
                    <animate attributeName="r" values="1.5;2;1.5" dur="0.6s" repeatCount="indefinite"/>
                </circle>
                <path d="M4 4H6L9 15H17L20 8H8" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <animateTransform attributeName="transform" type="translate" values="0 0; 1 -1; 0 0" dur="0.6s" repeatCount="indefinite"/>
                </path>
            </g>
        </svg>
    </div>
    """
    # Logo and header
    st.markdown("""
    <div class="logo-header">
        <div class="logo-icon">🛒</div>
        <h1>Smart Retail</h1>
        <p class="subtitle">Shop smarter, faster, easier</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom container for fingerprint authentication
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Fingerprint Authentication</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin: 15px 0;">Place your finger on the scanner</p>', unsafe_allow_html=True)
    
    # Fingerprint scanning animation
    fingerprint_base64 = get_base64_encoded_image("assets/fingerprint.jpg")
    
    scan_container = st.empty()
    scan_container.markdown(f"""
        <div class="fingerprint-container">
            <img src='{fingerprint_base64}' class="fingerprint-scan" />
            <div class="scan-line"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar for scan
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("<p style='text-align: center;'>Scanning fingerprint...</p>", unsafe_allow_html=True)
    
    # Simulate scanning progress
    for i in range(101):
        progress_bar.progress(i)
        if i < 30:
            status_text.markdown("<p style='text-align: center;'>Scanning fingerprint...</p>", unsafe_allow_html=True)
        elif i < 60:
            status_text.markdown("<p style='text-align: center;'>Analyzing print pattern...</p>", unsafe_allow_html=True)
        elif i < 90:
            status_text.markdown("<p style='text-align: center;'>Verifying ...</p>", unsafe_allow_html=True)
        else:
            status_text.markdown("<p style='text-align: center;'>Authenticating...</p>", unsafe_allow_html=True)

    # Fetch all users with fingerprint IDs
    users = db.collection("users").get()
    fingerprint_users = [user.to_dict() for user in users if "fingerprint_id" in user.to_dict()]

    if not fingerprint_users:
        st.error("No fingerprint-enabled users found.")
        return

    # Pick one user randomly for now (simulate fingerprint match)
    matched_user = random.choice(fingerprint_users)
    st.session_state["user_name"] = matched_user["name"]
    st.session_state["user_email"] = matched_user["email"]
    st.session_state["fingerprint_id"] = matched_user["fingerprint_id"]

    time.sleep(2)
    status_text.markdown("<p style='text-align: center;'>Authentication successful!.....</p>", unsafe_allow_html=True)
    time.sleep(0.05)  # Adjust speed of scan

    # Success message
    st.toast("Authentication successful! Redirecting to store...")
    
    # Remove scan line after completion
    scan_container.markdown(f"""
        <div class="fingerprint-container">
            <img src='{fingerprint_base64}' class="fingerprint-scan" />
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(4)  
    
    loading_placeholder = st.empty()
    loading_placeholder.markdown(loading_svg, unsafe_allow_html=True)

    # Dynamic Loading Text Updates
    time.sleep(1)
    status_text.markdown("<h3 style='text-align: center;'>Entering Store...</h3>", unsafe_allow_html=True)
    time.sleep(1)
    # Clear loading animations
    loading_placeholder.empty()
    status_text.empty()

    
    # Redirect to dashboard
    st.switch_page("pages/Customer_dashboard.py")
    
    # Back button (will only show if redirect fails)
    if st.button("Back to Login"):
        st.session_state.fingerprint = False
        st.session_state.user_registered = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

        
def main():
    if st.session_state.fingerprint:
        fingerprint_auth()
    elif st.session_state.user_registered is None:
        login_page()
    elif st.session_state.user_registered == "New User":
        register()
    elif st.session_state.user_registered == "Existing":
        authenticate()

main()