import streamlit as st
import pandas as pd

from utils import fetch_lbins, fetch_bazaar, expected_profit

st.title("Skyblock Gift Profit Calculator")

bazaar = fetch_bazaar()

# -----------------------------
# Sidebar Inputs
# -----------------------------

st.sidebar.header("Inputs")

snow_minion_t11_price = st.sidebar.number_input(
    "Snow Minion T11 Price",
    value=250000
)

st.sidebar.subheader("Coin Bonuses")

gold_talisman = st.sidebar.checkbox("Gold Gift Talisman (+25%)")
carnival = st.sidebar.checkbox("Carnival (+10%)")
snowman_mask = st.sidebar.checkbox("Snowman Mask (+10%)")

coin_bonus = 1 + (
    (0.25 if gold_talisman else 0) +
    (0.10 if carnival else 0) +
    (0.10 if snowman_mask else 0)
)

st.sidebar.write(f"Multiplier: {coin_bonus:.2f}x")
st.sidebar.subheader("Co-op Settings")
coop_bool = st.sidebar.checkbox("Opening with Coop")
coop = 1 + int(coop_bool)

st.sidebar.subheader("North Stars")
north_star_override = st.sidebar.checkbox("Include North Stars")

# -----------------------------
# LBIN Prices
# -----------------------------

lbin_items = {
    'CRYOPOWDER_SHARD',
    'GIFT_THE_FISH',
    'GOLD_GIFT',
    'KRAMPUS_HELMET',
    'NEW_BOTTLE_OF_JYRRE',
    'PET_SNOWMAN',
    'WINTER_ISLAND'
}

lbin_prices = fetch_lbins(lbin_items)

lbin_prices['Snow Minion'] = (
    snow_minion_t11_price
    - bazaar['ENCHANTED_SNOW_BLOCK']['Sell'] * 248
    - bazaar['SNOW_BLOCK']['Sell'] * 992
)

# -----------------------------
# North Stars
# -----------------------------

north_star_price = min(
    bazaar['ENCHANTMENT_LUCK_6']['Buy'],
    bazaar['ENCHANTMENT_SCAVENGER_4']['Buy'],
    bazaar['ENCHANTMENT_LOOTING_4']['Buy']
) / 10

north_stars_expected_value = {
    "white": north_star_price * 0.1,
    "green": north_star_price * 0.6,
    "red": north_star_price * 1.5
}

files = {
    "white": "white.csv",
    "green": "green.csv",
    "red": "red.csv"
}

# -----------------------------
# Calculate
# -----------------------------

if st.button("Calculate Expected Profits"):

    results = []

    for color, file in files.items():
        if file is None:
            continue

        df = pd.read_csv(file)

        expected = coop * expected_profit(
            color,
            df,
            lbin_prices,
            bazaar,
            coin_bonus
        ) + coop * north_stars_expected_value[color] * int(north_star_override)

        bazaar_price = bazaar[f"{color.upper()}_GIFT"]["Sell"]
        profit = expected - bazaar_price
        hourly_profit = expected * 256 * 60

        results.append({
            "Gift Color": color.capitalize(),
            "Bazaar Price": bazaar_price,
            "Expected Value": expected,
            "Profit per gift": profit,
            "Hourly Profit": hourly_profit
        })

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Format numbers with commas
    results_df[["Bazaar Price", "Expected Value", "Profit per gift", "Hourly Profit"]] = \
        results_df[["Bazaar Price", "Expected Value", "Profit per gift", "Hourly Profit"]].applymap(lambda x: f"{x:,.0f}")

    st.subheader("Expected Profits")
    st.dataframe(results_df, use_container_width=True)