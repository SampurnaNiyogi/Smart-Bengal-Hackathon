import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"

# Details about retailer and branch 
if "retail" in st.session_state:
    retail = st.session_state['retail']

if "branch" in st.session_state:
    branch = st.session_state['branch']

st.text_input("   Search Product   ")
response = requests.get(f"{BASE_URL}/{retail}/{branch}/get_product")
    
