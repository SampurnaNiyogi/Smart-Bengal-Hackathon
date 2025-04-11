import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"

# Check for user ID
if "user_name" not in st.session_state:
    st.error("Please log in to view your cart.")
    st.stop()

user_id = st.session_state["user_name"]  # or st.session_state["user_id"] if you store that

st.title(f"{user_id}'s Cart")

# Fetch cart data
response = requests.get(f"{BASE_URL}/{user_id}/get_cart")

if response.status_code == 200:
    cart = response.json()
    
    if not cart:
        st.info("Your cart is empty.")
    else:
        total = 0
        for product, details in cart.items():
            st.write(f"🛍 **{product.capitalize()}**")
            st.write(f"Quantity: {details['quantity']}")
            st.write(f"Price per item: ₹{details['price']}")
            st.write("---")
            total += details['quantity'] * details['price']

        st.subheader(f"🧾 Total: ₹{total}")

else:
    st.error("Failed to fetch cart.")
