import streamlit as st
import requests
import urllib.parse
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time

import platform
import os
from utils import load_css
import ctypes

# Only for macOS
if platform.system() == "Darwin":
    lib_path = "/opt/homebrew/opt/zbar/lib/libzbar.dylib"
    if os.path.exists(lib_path):
        ctypes.cdll.LoadLibrary(lib_path)
    else:
        raise FileNotFoundError(f"ZBar library not found at {lib_path}")

# from store_map import render_store_map

# # Navigation
# page = st.sidebar.selectbox("Go to", ["Store Map", "Products"])
# if page == "Store Map":
#     render_store_map()

if 'retail' not in st.session_state or not st.session_state['retail']:
    st.error("Please login/register to view the search dashboard", icon=':material/error:')
    st.stop()

# Inject custom CSS to hide Streamlit's default UI
search_css = load_css('search-dashboard.css')
st.markdown(search_css, unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:5000"

# Title
st.markdown('<div class="page-title">Product Search</div>', unsafe_allow_html=True)

# Retailer Info
provider = st.session_state.get('retail', "Unknown Retailer")
branch = st.session_state.get('branch', "Unknown Branch")

# Store Info Banner
st.markdown(f"""
<div class="store-info">
    <div style="font-weight: 600; color: #3498db;">{provider}</div>
    <div style="color: #7f8c8d;">{branch} Branch</div>
</div>
""", unsafe_allow_html=True)


# ------------------- Barcode Scanner --------------------

def scan_barcode_streamlit():
    scanned_id = ""
    cap = cv2.VideoCapture(0)
    FRAME_WINDOW = st.image([])

    status_placeholder = st.empty()
    status_placeholder.info("📸 Scanning... Show the barcode to your webcam")

    # Use session state to track cancel
    if "cancel_scan" not in st.session_state:
        st.session_state["cancel_scan"] = False

    # Place cancel button outside loop
    cancel = st.button("Cancel Scan", icon='❌')

    while cap.isOpened():
        if st.session_state["cancel_scan"] or cancel:
            st.session_state["cancel_scan"] = True
            break

        success, frame = cap.read()
        if not success:
            st.error('Camera cannot capture video')
            break

        # Decode only 2 types of barcodes used in retail
        decoded_objects = decode(frame, symbols=[ZBarSymbol.EAN8, ZBarSymbol.EAN13])
        if decoded_objects:
            scanned_id = decoded_objects[0].data.decode('utf-8').strip()
            break

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        FRAME_WINDOW.image(frame, channels="BGR")
        time.sleep(0.05)  # Slight delay to reduce CPU usage

    cap.release()
    cv2.destroyAllWindows()
    FRAME_WINDOW.empty()

    st.session_state["cancel_scan"] = False
    status_placeholder.empty()
    return scanned_id


# Scan Button
if st.button("📷 Scan Barcode"):
    product_id = scan_barcode_streamlit()

    if product_id:
        st.success(f"✅ Scanned: {product_id}")
        st.session_state["scan_time"] = time.time()

        # API call
        try:
            response = requests.get(f"{BASE_URL}/{provider}/{branch}/{product_id}/get_product_by_barcode")
            if response.status_code == 200:
                product_data = response.json()
                st.session_state["scanned_product"] = product_data["product_name"]

            else:
                st.error("❌ Product not found for this barcode.")
        except Exception as e:
            st.error(f"⚠️ Error fetching product")
            st.text(f"{e}")
    else:
        st.error("❌ No barcode detected")

# Auto-clear scanned_product after 10 seconds
if "scan_time" in st.session_state and time.time() - st.session_state["scan_time"] > 10:
    st.session_state.pop("scanned_product", None)
    st.session_state.pop("scan_time", None)

# -------------------- Search Input ---------------------

st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
st.markdown('<span class="search-icon">🔍</span>', unsafe_allow_html=True)

product_name = st.text_input("Search Product",
                             label_visibility="collapsed",
                             placeholder="Search for products...",
                             value=st.session_state.get("scanned_product", ""))

st.markdown('</div>', unsafe_allow_html=True)

# ------------------- Product Fetch & Display -------------------

if product_name:
    encoded_branch = urllib.parse.quote(branch)
    encoded_product = urllib.parse.quote(product_name.lower())

    try:
        response = requests.get(f"{BASE_URL}/{provider}/{encoded_branch}/{encoded_product}/get_product")
        if response.status_code == 200:
            product_details = response.json()
            st.markdown("### 🛍️ Product Details")

            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"#### 🧾 {product_name.title()}")
                    st.markdown(f"**📦 Availability:** `{product_details['quantity']} in stock`")
                    st.markdown(f"**💰 Price:** `₹{product_details['price']}`")

                with col2:
                    if "scanned_product" in st.session_state:
                        if product_details['quantity'] == 0:
                            st.info("Product Not Available")
                            st.button("➕ Add to Cart", disabled=True)
                        else:
                            quantity = st.number_input("Quantity",
                                                       min_value=1,
                                                       max_value=product_details['quantity'],
                                                       value=1,
                                                       step=1,
                                                       key="quantity_input")
                            if st.button("➕ Add to Cart", use_container_width=True):
                                user_id = st.session_state.get("user_name", "guest")
                                add_response = requests.post(
                                    f"{BASE_URL}/{provider}/{encoded_branch}/{user_id}/add_to_cart",
                                    json={
                                        "product_name": product_name.lower(),
                                        "quantity": quantity,
                                        "price": product_details["price"]
                                    }
                                )
                                if add_response.status_code == 200:
                                    st.success(f"✅ {product_name.title()} added to cart!")
                                    time.sleep(1)
                                    st.session_state.pop("scanned_product", None)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to add: {add_response.json().get('error')}")
                    else:
                        st.warning("Scan Product first to add to cart")
                        st.rerun()
        elif response.status_code == 400:
            st.markdown("""
            <div class="error-message">
                <strong>Product Not Found</strong><br>
                We couldn't find the product you're looking for. 
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error("⚠️ Unable to fetch product info")
        st.text(str(e))

# ------------------- Navigation Buttons -------------------

col1, col2 = st.columns([2, 1])
with col1:
    if st.button("⬅️ Back to Home"):
        st.switch_page("pages/3_👥_Dashboard.py")
with col2:
    if st.button("🛒 View Cart"):
        st.switch_page("pages/5_🛒_Cart_Dashboard.py")
