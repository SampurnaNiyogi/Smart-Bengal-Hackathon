import streamlit as st
import requests
import urllib.parse
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import time

# from store_map import render_store_map

# # Navigation
# page = st.sidebar.selectbox("Go to", ["Store Map", "Products"])
# if page == "Store Map":
#     render_store_map()

# Custom CSS
st.markdown("""
<style>
    .main-container {
        padding: 1.5rem;
    }
    
    .page-title {
        font-size: 2rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white;
        padding: 0.8rem;
        border-radius: 10px;
    }
    
    .search-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .product-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3498db;
        margin-top: 1rem;
    }
    
    .product-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .product-detail {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f1f1;
    }
    
    .detail-label {
        font-weight: 500;
        color: #7f8c8d;
    }
    
    .detail-value {
        font-weight: 600;
        color: #2c3e50;
    }
    
    .price-value {
        color: #27ae60;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .quantity-container {
        margin-top: 1rem;
        padding: 1rem 0;
    }
    
    .add-button {
        background-color: #27ae60 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        margin-top: 1rem !important;
    }
    
    .store-info {
        padding: 0.8rem;
        background-color: #e8f4f8;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .back-button {
        margin-top: 1rem;
    }
    
    /* Style for the search input */
    .stTextInput > div > div > input {
        border-radius: 20px !important;
        padding-left: 2.5rem !important;
        font-size: 1rem !important;
        border: 2px solid #f1f1f1 !important;
    }
    
    .search-icon {
        position: absolute;
        left: 0.8rem;
        top: 0.5rem;
        color: #95a5a6;
        font-size: 1.2rem;
        z-index: 1;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 5px !important;
    }
    
    .error-message {
        background-color: #fdeded;
        color: #ef5350;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ef5350;
        margin: 1rem 0;
    }
    
    .success-message {
        background-color: #edf7ed;
        color: #4caf50;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


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
        st.switch_page("pages/Customer_dashboard.py")
with col2:
    if st.button("🛒 View Cart"):
        st.switch_page("pages/Cart_dashboard.py")
