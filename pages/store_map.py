import folium
import streamlit as st
from streamlit_folium import st_folium

# Custom Sidebar Styling

# Hide default Streamlit sidebar & footer

# Inject custom CSS to hide Streamlit's default UI


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
st_folium(m, width=1000, height=700)
