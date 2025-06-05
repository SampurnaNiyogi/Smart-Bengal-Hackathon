from streamlit import cache_data, Page, navigation
from typing import NoReturn


@cache_data
def get_page_list():
    return [
        Page('subpages/home.py', title='Home', icon='🏠'),
        Page('subpages/login.py', title='Login', url_path='login', icon='🔐'),
        Page('subpages/customer_dashboard.py', title='Customer Dashboard',
             url_path='customer_dashboard', icon='👥'),
        Page('subpages/search_dashboard.py', title='Search Dashboard',
             url_path='search_dashboard', icon='🔎'),
        Page('subpages/cart_dashboard.py', title='Cart Dashboard', url_path='cart_dashboard', icon='🛒'),
        Page('subpages/payment_page.py', title='Payment Page', url_path='payment_page', icon='💳'),
        Page('subpages/store_map.py', title='Store Map', url_path='store_map', icon='🗺️')
    ]


page_list = get_page_list()
navigation(page_list).run()
