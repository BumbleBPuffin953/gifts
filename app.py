import streamlit as st
import pandas as pd
from utils import fetch_recent_avg, fetch_bazaar, expected_value

st.title("Skyblock Gift Profit Calculator")

# Fetch live prices
bazaar = fetch_bazaar()
lbin_items = {
    'CRYOPOWDER_SHARD', 'GOLD_GIFT', 'KRAMPUS_HELMET',
    'NEW_BOTTLE_OF_JYRRE', 'PET_SNOWMAN', 'WINTER_ISLAND',
    "PARTY_THE_FISH", "PARTY_HAT", "PARTY_GLOVES",
    "PARTY_CLOAK", "SNOWMAN_MASK"
}
lbin_prices = fetch_recent_avg(lbin_items)

# North star expected value
north_star_price = (
    bazaar['ENCHANTMENT_LUCK_6']['Buy'] +
    bazaar['ENCHANTMENT_SCAVENGER_4']['Buy'] +
    bazaar['ENCHANTMENT_LOOTING_4']['Buy']
) / 30

north_stars_expected_value = {
    "white": north_star_price * 0.1,
    "green": north_star_price * 0.6,
    "red": north_star_price * 1.5
}

# Gift CSV files
gift_files = {
    "white": "white.csv",
    "green": "green.csv",
    "red": "red.csv",
    "party": "party.csv"
}

# --------------------------
# Sidebar Form
# --------------------------
with st.sidebar.form("settings_form"):
    st.subheader("Coin Bonuses")
    gold_talisman = st.checkbox("Gold Gift Talisman (+25%)")
    carnival = st.checkbox("Carnival (+10%)")
    snowman_mask = st.checkbox("Snowman Mask (+10%)")
    north_star_override = st.checkbox("Include North Stars")
    coop_bool = st.checkbox("Item Toggle")
    submitted = st.form_submit_button("Calculate Expected Profits")

# --------------------------
# Only calculate when form submitted
# --------------------------
if submitted:
    # Compute multipliers
    coin_bonus = 1 + (
        (0.25 if gold_talisman else 0) +
        (0.10 if carnival else 0) +
        (0.10 if snowman_mask else 0)
    )
    coop = 1 + int(coop_bool)

    # Two result tables
    sell_results = []
    buy_results = []

 # Calculate expected profits for each gift type
    for color, file in gift_files.items():
        df = pd.read_csv(file)
        ev = expected_value(df, lbin_prices, coin_bonus)

        if north_star_override and color in north_stars_expected_value:
            ev += north_stars_expected_value[color]

        sell_price = bazaar[f"{color.upper()}_GIFT"]["Sell"] / coop 
        buy_price = bazaar[f"{color.upper()}_GIFT"]["Buy"] / coop

        # --- SELL TABLE ---
        sell_profit = ev - sell_price
        sell_hourly = sell_profit * 192 * 60

        sell_results.append({
            "Gift Color": color.capitalize(),
            "Bazaar Sell Price": f"{sell_price:,.0f}",
            "Expected Value": f"{ev:,.0f}",
            "Profit per Gift": f"{sell_profit:,.0f}",
            "Profit Per Inventory": f"{sell_hourly:,.0f}"
        })

        # --- BUY TABLE ---
        buy_profit = ev - buy_price
        buy_hourly = buy_profit * 192 * 60

        buy_results.append({
            "Gift Color": color.capitalize(),
            "Bazaar Buy Price": f"{buy_price:,.0f}",
            "Expected Value": f"{ev:,.0f}",
            "Profit per Gift": f"{buy_profit:,.0f}",
            "Profit Per Hour": f"{buy_hourly:,.0f}"
        })


    st.subheader("Expected Profits (Sell Price)")
    st.dataframe(pd.DataFrame(sell_results), use_container_width=True)

    st.subheader("Expected Profits (Buy Price)")
    st.dataframe(pd.DataFrame(buy_results), use_container_width=True)