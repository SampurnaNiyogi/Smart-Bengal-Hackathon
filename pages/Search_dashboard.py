import streamlit as st
import requests
import urllib.parse

BASE_URL = "http://127.0.0.1:5000"

# Details about retailer and branch 
if "retail" in st.session_state:
    provider = st.session_state['retail']

if "branch" in st.session_state:
    branch = st.session_state['branch']

product_name = st.text_input("   Search Product   ")

encoded_branch = urllib.parse.quote(branch)
encoded_product = urllib.parse.quote(product_name)

response = requests.get(f"{BASE_URL}/{provider}/{encoded_branch}/{encoded_product}/get_product")



 
if response.status_code == 200:
    st.write("Product Found")
    product_details = response.json()
    st.write(f"Quantity : {product_details['Quantity']}")
    st.write(f"Loaction : {product_details['Location']}")

else:
    st.error("No product found")


