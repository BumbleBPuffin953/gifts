import pandas as pd
import requests


def fetch_lbins(item_ids):

    def get_price(item):
        data = requests.get(
            f"https://sky.coflnet.com/api/auctions/tag/{item}/active/bin"
        ).json()
        return data[0]["startingBid"] if data else 0

    return {item: get_price(item) for item in item_ids}


def fetch_bazaar():
    r = requests.get("https://api.hypixel.net/v2/skyblock/bazaar").json()

    return {
        k: {
            "Sell": v["quick_status"]["sellPrice"],
            "Buy": v["quick_status"]["buyPrice"]
        }
        for k, v in r["products"].items()
    }


def apply_price_overrides(df, price_map, coin_bonus, weight_col="Weight", price_col="Price"):

    df = df.copy()

    df[price_col] *= coin_bonus

    mask = df["Item"].isin(price_map)
    df.loc[mask, price_col] = df.loc[mask, "Item"].map(price_map)

    weights = df[weight_col]
    factor = weights / weights.sum()

    df[price_col] *= factor

    return df


def expected_profit(color, df, price_map, bazaar, coin_bonus):

    df = apply_price_overrides(df, price_map, coin_bonus)

    profit = 2 * df["Price"].sum() - bazaar[f"{color.upper()}_GIFT"]["Sell"]

    return profit