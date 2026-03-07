import streamlit as st
import pandas as pd
from utils import fetch_lbins, fetch_bazaar, expected_value

st.title("Skyblock Gift Profit Calculator")

# Fetch live prices
bazaar = fetch_bazaar()
lbin_items = {
    'CRYOPOWDER_SHARD', 'GOLD_GIFT', 'KRAMPUS_HELMET',
    'NEW_BOTTLE_OF_JYRRE', 'PET_SNOWMAN', 'WINTER_ISLAND',
    "PARTY_THE_FISH", "PARTY_HAT", "PARTY_GLOVES",
    "PARTY_CLOAK", "SNOWMAN_MASK"
}
lbin_prices = fetch_lbins(lbin_items)

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

    st.subheader("Co-op Settings")
    coop_bool = st.checkbox("Opening with Coop")

    st.subheader("Toggles")
    north_star_override = st.checkbox("Include North Stars")
    include_snow_minion = st.checkbox("Include Snow Minion")
    snow_minion_t1_price = st.number_input(
        "Snow Minion T1 Price",
        value=50_000
    )
    coins_only = st.checkbox("Coins Only")

    # Submit button inside the form
    st.markdown(f"North Stars Value: {north_star_price:,.0f}")
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

    # Include snow minion if toggled
    if include_snow_minion:
        lbin_prices['Snow Minion'] = snow_minion_t1_price

    if coins_only:
        for item in lbin_prices:
            lbin_prices[item] = 0

    # Calculate expected profits for each gift type
    results = []
    for color, file in gift_files.items():
        df = pd.read_csv(file)
        ev = expected_value(df, lbin_prices, coin_bonus)

        if north_star_override and color in north_stars_expected_value:
            ev += north_stars_expected_value[color]

        ev *= coop
        gift_price = bazaar[f"{color.upper()}_GIFT"]["Sell"]
        profit = ev - gift_price
        hourly_profit = profit * 2240

        results.append({
            "Gift Color": color.capitalize(),
            "Bazaar Price": f"{gift_price:,.0f}",
            "Expected Value": f"{ev:,.0f}",
            "Profit per Gift": f"{profit:,.0f}",
            "Profit Per Inventory": f"{hourly_profit:,.0f}"
        })

    st.subheader("Expected Profits")
    st.dataframe(pd.DataFrame(results), use_container_width=True)

# --------------------------
# LBIN Prices table
# --------------------------
st.subheader("LBIN Prices")
lbin_df = pd.DataFrame(list(lbin_prices.items()), columns=["Item", "Price"])
lbin_df["Price"] = lbin_df["Price"].apply(lambda x: f"{x:,.0f}")
st.dataframe(lbin_df, use_container_width=True)