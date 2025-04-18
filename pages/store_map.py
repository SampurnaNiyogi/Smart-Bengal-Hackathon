import streamlit as st
import folium
from streamlit_folium import folium_static




# Custom Sidebar Styling
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(145deg, #1f1f2f, #191926);
            padding-top: 2rem;
            transition: all 0.3s ease-in-out;
        }
        [data-testid="stSidebar"]:hover {
            background: linear-gradient(145deg, #292940, #1f1f2f);
        }
        [data-testid="stSidebar"] * {
            color: #f0f0f0 !important;
            font-family: 'Segoe UI', sans-serif;
        }
        .stSelectbox > div {
            padding: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    page = st.selectbox("📂 Navigate to", [
        "🏠 Main",
        "🛒 Cart Dashboard",
        "👥 Customer Dashboard",
        "🔐 Login",
        "💳 Payment Page",
        "🔎 Search Dashboard",
        "🗺️ Store Map"
    ])

# Route (manual redirect if all logic is in main.py)
if page == "🏠 Main":
    st.title("")
elif page == "🛒 Cart Dashboard":
    st.switch_page("pages/Cart_Dashboard.py")
elif page == "👥 Customer Dashboard":
    st.switch_page("pages/Customer_Dashboard.py")
elif page == "🔐 Login":
    st.switch_page("pages/Login.py")
elif page == "💳 Payment Page":
    st.switch_page("pages/Payment_page.py")
elif page == "🔎 Search Dashboard":
    st.switch_page("pages/Search_Dashboard.py")
elif page == "🗺️ Store Map":
    st.switch_page("pages/Store_map.py")

# Hide default Streamlit sidebar & footer
st.markdown("""
    <style>
        /* Hide top-right hamburger menu */
        #MainMenu {visibility: hidden;}
        
        /* Hide footer */
        footer {visibility: hidden;}
        
        /* Optional: Hide sidebar toggle completely */
        .css-1d391kg {display: none}
    </style>
""", unsafe_allow_html=True)




st.set_page_config(layout="wide")
st.title("🗺️ Interactive Store Map with Folium")

# Define map center and zoom
m = folium.Map(location=[0, 0], zoom_start=17, width='100%', height='100%')

# Helper to add store section blocks (rectangles)
def add_section(map_obj, name, top_left, bottom_right, color, items):
    folium.Rectangle(
        bounds=[top_left, bottom_right],
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=folium.Popup(f"<b>{name}</b><br>" + "<br>".join(items), max_width=200)
    ).add_to(map_obj)

# Define layout blocks with fake lat/long (since it's indoor, just schematic values)
store_sections = [
    ("Bakery", [0.002, -0.004], [0, -0.002], "#f59e0b", ["Bread", "Croissants"]),
    ("Dairy and Eggs", [0.002, -0.002], [0, 0], "#3b82f6", ["Milk", "Eggs", "Cheese"]),
    ("Snacks", [0.002, 0], [0, 0.002], "#10b981", ["Chips", "Cookies"]),
    ("Meat", [0.002, 0.002], [0, 0.004], "#ef4444", ["Chicken", "Beef"]),
    ("Frozen Foods", [0.002, 0.004], [0, 0.006], "#6366f1", ["Ice Cream", "Frozen Pizza"]),
    ("Beverages", [0.002, 0.006], [0, 0.008], "#ec4899", ["Soda", "Juice"]),
    ("Fresh Fruits / Vegetables", [-0.002, -0.004], [-0.004, -0.002], "#84cc16", ["Apples", "Carrots"]),
    ("Cleaning / Pet Supplies", [-0.002, -0.002], [-0.004, 0], "#a855f7", ["Detergent", "Pet Food"]),
    ("Checkout Area", [-0.002, 0.004], [-0.004, 0.008], "#f97316", ["Scan Station", "Payment"])
]

# Draw sections
for name, top_left, bottom_right, color, items in store_sections:
    add_section(m, name, top_left, bottom_right, color, items)

# Draw some paths (for walking flow)
paths = [
    ([0.001, -0.003], [0.001, 0.007]),  # main top path
    ([-0.003, -0.003], [-0.003, 0.007]),  # main bottom path
    ([0.001, 0.007], [-0.003, 0.007]),  # right connector
]

for start, end in paths:
    folium.PolyLine([start, end], color="gray", dash_array='5').add_to(m)

# Display the Folium map
folium_static(m, width=1000, height=700)
