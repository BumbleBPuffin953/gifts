import streamlit as st
import pandas as pd
from utils import fetch_lbins, fetch_bazaar, expected_value

st.set_page_config(page_title="Skyblock Gift Profit Calculator", layout="wide")
st.title("Skyblock Gift Profit Calculator")

# -----------------------------
# Fetch Bazaar and LBIN prices
# -----------------------------
bazaar = fetch_bazaar()

lbin_items = {
    'CRYOPOWDER_SHARD',
    'GOLD_GIFT',
    'KRAMPUS_HELMET',
    'NEW_BOTTLE_OF_JYRRE',
    'PET_SNOWMAN',
    'WINTER_ISLAND',
    "PARTY_THE_FISH",
    "PARTY_HAT",
    "PARTY_GLOVES",
    "PARTY_CLOAK",
    "SNOWMAN_MASK"
}
lbin_prices = fetch_lbins(lbin_items)

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Inputs")

# Coin bonuses
st.sidebar.subheader("Coin Bonuses")
gold_talisman = st.sidebar.checkbox("Gold Gift Talisman (+25%)")
carnival = st.sidebar.checkbox("Carnival (+10%)")
snowman_mask = st.sidebar.checkbox("Snowman Mask (+10%)")

coin_bonus = 1 + (
    (0.25 if gold_talisman else 0) +
    (0.10 if carnival else 0) +
    (0.10 if snowman_mask else 0)
)
st.sidebar.write(f"Coin Multiplier: {coin_bonus:.2f}x")

# Co-op
st.sidebar.subheader("Co-op Settings")
coop_bool = st.sidebar.checkbox("Opening with Coop")
coop = 1 + int(coop_bool)

# Other toggles
st.sidebar.subheader("Toggles")
north_star_override = st.sidebar.checkbox("Include North Stars")
include_snow_minion = st.sidebar.checkbox("Include Snow Minion")
snow_minion_t11_price = st.sidebar.number_input(
    "Snow Minion T11 Price",
    value=250_000
)

if include_snow_minion:
    lbin_prices['Snow Minion'] = (
        snow_minion_t11_price
        - bazaar['ENCHANTED_SNOW_BLOCK']['Sell'] * 248
        - bazaar['SNOW_BLOCK']['Sell'] * 992
    )

# North Star EV calculation
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

# CSV files for gift tables
gift_files = {
    "white": "white.csv",
    "green": "green.csv",
    "red": "red.csv",
    "party": "party.csv"
}

# -----------------------------
# Calculate Expected Profits
# -----------------------------
if st.button("Calculate Expected Profits"):

    results = []

    for color, file in gift_files.items():
        df = pd.read_csv(file)

        # Compute expected value
        ev = expected_value(df, lbin_prices, coin_bonus)

        # Include North Star value if enabled
        if north_star_override and color in north_stars_expected_value:
            ev += north_stars_expected_value[color]

        # Apply co-op multiplier
        ev *= coop

        # Bazaar price of the gift
        gift_price = bazaar[f"{color.upper()}_GIFT"]["Sell"]

        # Profit calculations
        profit_per_gift = ev - gift_price
        hourly_profit = profit_per_gift * 256 * 60  # 256 gifts per minute

        results.append({
            "Gift Color": color.capitalize(),
            "Bazaar Price": f"{gift_price:,.0f}",
            "Expected Value": f"{ev:,.0f}",
            "Profit per Gift": f"{profit_per_gift:,.0f}",
            "Hourly Profit": f"{hourly_profit:,.0f}"
        })

    # Display results
    st.subheader("Expected Profits")
    st.dataframe(pd.DataFrame(results), use_container_width=True)

# -----------------------------
# Display LBIN Prices
# -----------------------------
st.subheader("LBIN Prices")
lbin_df = pd.DataFrame(list(lbin_prices.items()), columns=["Item", "Price"])
lbin_df["Price"] = lbin_df["Price"].apply(lambda x: f"{x:,.0f}")
st.dataframe(lbin_df, use_container_width=True)