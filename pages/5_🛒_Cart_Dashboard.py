import streamlit as st
import requests
import time
import urllib.parse





# Hide default Streamlit sidebar & footer

# Inject custom CSS to hide Streamlit's default UI




BASE_URL = "http://127.0.0.1:5000"

# Session check
if "user_name" not in st.session_state:
    st.error("🚫 Please log in to view your cart.")
    st.stop()

user_id = st.session_state["user_name"]

st.markdown(f"<h2 style='text-align: center;'>🛒 {user_id}'s Shopping Cart</h2>", unsafe_allow_html=True)
st.markdown("---")
# Details about retailer and branch 
if "retail" in st.session_state:
    provider = st.session_state['retail']
else:
    provider = "Unknown Retailer"

if "branch" in st.session_state:
    branch = st.session_state['branch']
else:
    branch = "Unknown Branch"

encoded_branch = urllib.parse.quote(branch)

# Fetch cart
response = requests.get(f"{BASE_URL}/{user_id}/get_cart")

if response.status_code == 200:
    cart = response.json()
    
    if not cart:
        st.info("🛍️ Your cart is currently empty.")
    else:
        total = 0

        for product, details in cart.items():
            encoded_product = urllib.parse.quote(product.lower())
            response_product = requests.get(f"{BASE_URL}/{provider}/{encoded_branch}/{encoded_product}/get_product")
            if response.status_code == 200:
                product_details = response_product.json()
                available_stock = product_details.get("quantity", 0)
                current_cart_qty = details["quantity"]
                max_stock = current_cart_qty + available_stock
            with st.container():
                st.markdown("#### 🧾 " + product.title())
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Price per item:** ₹{details['price']}")
                    st.write(f"**Current quantity:** {details['quantity']}")

                    new_qty = st.number_input(
                        f"Update quantity for {product}",
                        min_value=0,
                        max_value=max_stock,
                        value=details["quantity"],
                        key=product
                    )

                    if new_qty != details["quantity"]:
                        if st.button(f"Update {product}", key=f"btn_{product}"):
                            update = requests.post(
                                f"{BASE_URL}/{user_id}/update_cart_item",
                                json={"provider": provider, "branch": encoded_branch, "product_details":{"product_name": product, "quantity": new_qty}}
                            )
                            if update.status_code == 200:
                                st.success(f"✅ {product.title()} updated successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to update cart.")
                    
                with col2:
                    item_total = new_qty * details['price']
                    st.markdown(f"### ₹{item_total:.2f}")
                    total += item_total

                st.markdown("---")

        # Cart Total
        st.markdown(f"<h3 style='text-align:right;'>🧾 Total: ₹{total:.2f}</h3>", unsafe_allow_html=True)

        # Checkout button
        st.markdown("### ")
        if st.button("✅ Proceed to Checkout", use_container_width=True):
            checkout_payload = {
                "provider": st.session_state.get("retail", ""),
                "branch": st.session_state.get("branch", "")
            }
            st.session_state["checkout_payload"] = {
            "provider": st.session_state["retail"],
            "branch": st.session_state["branch"]
            }
            st.switch_page("pages/6_💳_Payment_Page.py")    
            st.rerun()
        
          
else:
    st.error("❌ Failed to fetch cart.")
if st.button("Return to Search 🔍"):
    st.switch_page("pages/4_🔎_Search_Dashboard.py")
