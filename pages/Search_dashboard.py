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
encoded_product = urllib.parse.quote(product_name.lower())


response = requests.get(f"{BASE_URL}/{provider}/{encoded_branch}/{encoded_product}/get_product")


if response.status_code == 200:
    st.write("Product Found")
    product_details = response.json()
    st.write(f"Available Quantity : {product_details['quantity']}")
    st.write(f"Price : ₹{product_details['price']}")

    quantity = st.number_input("Select quantity", min_value=1, max_value=product_details['quantity'], value=1)

    if st.button("Add to Cart"):
        user_id = st.session_state.get("user_name", "guest")  # use name as ID for now

        add_response = requests.post(
            f"{BASE_URL}/{user_id}/add_to_cart",
            json={
                "product_name": product_name.lower(),
                "quantity": quantity,
                "price": product_details["price"]
            }
        )

        if add_response.status_code == 200:
            st.success(f"{product_name} added to cart!")
        else:
            st.error(f"Error adding to cart: {add_response.json().get('error')}")


if response.status_code == 400:
    st.error("No product found")