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
            st.markdown(f"### 🛍 {product.capitalize()}")
            st.write(f"Price per item: ₹{details['price']}")

            # Editable quantity input
            new_qty = st.number_input(
                f"Quantity for {product}", 
                min_value=0,  # allow 0 to mean delete
                value=details["quantity"], 
                key=product
            )

            if new_qty != details["quantity"]:
                if st.button(f"Update {product}", key=f"btn_{product}"):
                    update = requests.post(
                        f"{BASE_URL}/{user_id}/update_cart_item",
                        json={"product_name": product, "quantity": new_qty}
                    )
                    if update.status_code == 200:
                        st.success(f"{product} updated!")
                        st.rerun()
                    else:
                        st.error("Failed to update cart.")
            total += new_qty * details["price"]

        st.subheader(f"🧾 Total: ₹{total}")

else:
    st.error("Failed to fetch cart.")

if st.button("✅ Proceed to Checkout"):
    st.write("Provider:", st.session_state["retail"])
    st.write("Branch:", st.session_state["branch"])
    checkout_payload = {
        "provider": st.session_state["retail"],  # lowercase enforced in backend
        "branch": st.session_state["branch"]
    }

    response = requests.post(f"{BASE_URL}/{user_id}/checkout", json=checkout_payload)

    if response.status_code == 200:
        st.success("✅ Order placed successfully!")
        st.rerun()
    else:
        st.error(response.json().get("error", "Checkout failed."))

