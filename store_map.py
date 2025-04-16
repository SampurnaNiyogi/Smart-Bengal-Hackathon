import streamlit as st
import streamlit.components.v1 as components


def render_store_map():
	st.subheader("🛒 Store Layout")

	store_grid_html = """
    <style>
    .store-grid {
        display: grid;
        grid-template-columns: repeat(7, 80px);
        grid-gap: 10px;
        margin-top: 30px;
    }
    .cell {
        width: 80px;
        height: 80px;
        border-radius: 8px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        color: white;
        font-size: 12px;
        text-align: center;
        padding: 5px;
    }
    .cell.groceries { background-color: #4CAF50; }
    .cell.toiletries { background-color: #b39ddb; }
    .cell.snacks { background-color: #a1887f; }
    .cell.beverages { background-color: #81d4fa; color: black; }
    .cell.household { background-color: #90a4ae; }
    .cell.checkout { background-color: #f4b400; color: black; }
    .cell.entrance { background-color: #cfe2ff; color: black; }
    .cell.empty { background-color: #e0e0e0; color: black; }
    </style>

    <div class="store-grid">
        <div class="cell groceries">Groceries</div>
        <div class="cell toiletries">Toiletries</div>
        <div class="cell checkout">Checkout</div>
        <div class="cell entrance">Entrance</div>
        <div class="cell snacks">Snacks</div>
        <div class="cell beverages">Beverages</div>
        <div class="cell household">Household</div>

        <div class="cell empty"></div>
        <div class="cell groceries">Groceries</div>
        <div class="cell toiletries">Toiletries</div>
        <div class="cell snacks">Snacks</div>
        <div class="cell beverages">Beverages</div>
        <div class="cell household">Household</div>
        <div class="cell empty"></div>

        <div class="cell groceries">Groceries</div>
        <div class="cell empty"></div>
        <div class="cell empty"></div>
        <div class="cell snacks">Snacks</div>
        <div class="cell beverages">Beverages</div>
        <div class="cell household">Household</div>
        <div class="cell empty"></div>
    </div>
    """

	components.html(store_grid_html, height=350)
