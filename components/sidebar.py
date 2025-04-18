import streamlit as st


def vertical_navbar():
    st.markdown("""
    <style>
        .sidebar-custom {
            position: fixed;
            left: 0;
            top: 0;
            width: 220px;
            height: 100%;
            background-color: #1f1f2f;
            padding-top: 60px;
            z-index: 9999;
        }

        .sidebar-custom a {
            display: block;
            padding: 16px 25px;
            color: #ffffff;
            text-decoration: none;
            font-size: 16px;
            transition: background 0.3s;
        }

        .sidebar-custom a:hover {
            background-color: #33334d;
            color: #E8C999;
        }

        .main-content {
            margin-left: 240px;  /* Adjust based on sidebar width */
            padding: 20px;
        }

        /* Optional: Hide Streamlit sidebar */
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Hide Streamlit top-right hamburger and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="collapsedControl"] {display: none;}
    </style>

    <div class="sidebar-custom">
        <a href="/">🏠 Main</a>
        <a href="/Cart_Dashboard">🛒 Cart Dashboard</a>
        <a href="/Customer_Dashboard">👥 Customer Dashboard</a>
        <a href="/Login">🔐 Login</a>
        <a href="/Payment_page">💳 Payment Page</a>
        <a href="/Search_Dashboard">🔎 Search Dashboard</a>
        <a href="/Store_map">🗺️ Store Map</a>
    </div>
    """, unsafe_allow_html=True)
