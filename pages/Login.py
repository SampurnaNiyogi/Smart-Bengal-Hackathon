\import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get the JSON key path
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

def login_page():
    st.title("Login/Sign Up")
    if st.button("Sign In"):
        st.session_state.user_registered = "Existing"
        st.rerun()
    elif st.button("Sign Up"):
        st.session_state.user_registered = "New User"
        st.rerun()

def add_user(name, email):
    try:
        users_ref = db.collection("users")
        users_ref.add({"name": name, "email": email})
        st.session_state.user_registered = True
        return True
    except Exception as e:
        st.error(f"Error adding user: {e}")
        return False

def register():
    st.title("Sign Up")
    st.subheader("New User Sign Up")
    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")
    if st.button("Sign Up"):
        if add_user(name, email):
            st.success(f"User {name} added successfully!")
            st.session_state.page = "consumer_dashboard"
            st.session_state.user_registered = "Existing"
            status_placeholder = st.empty()
            with status_placeholder.status("Loading......"):
                for i in range(1):
                    time.sleep(1)
            status_placeholder.empty()
            st.rerun()

def authenticate():
    st.title("Sign In")
    u_name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")
    if st.button("Sign In"):
        user_ref = db.collection("users").where("name", "==", u_name).where("email", "==", email).get()
        if user_ref:
            st.session_state["user_name"] = u_name
            st.switch_page("pages/Customer_dashboard.py")
        else:
            st.error("Incorrect name or email")

if st.session_state.user_registered is None:
    login_page()
elif st.session_state.user_registered == "New User":
    register()
elif st.session_state.user_registered == "Existing":
    authenticate()
