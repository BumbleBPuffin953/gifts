import pandas as pd
import requests

def fetch_lbins(item_ids):
    def get_price(item):
        try:
            response = requests.get(
                f"https://sky.coflnet.com/api/auctions/tag/{item}/active/bin"
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("startingBid", 0)
            if isinstance(data, dict) and "auctions" in data and data["auctions"]:
                return data["auctions"][0].get("startingBid", 0)
            return 0
        except Exception as e:
            print(f"Error fetching {item}: {e}")
            return 0
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

def expected_value(df, lbin_prices, coin_bonus):
    total_weight = df["Weight"].sum()
    ev = 0
    for _, row in df.iterrows():
        item = row["Item"]
        weight = row["Weight"]
        base_price = row["Price"]

        p = weight / total_weight

        if item == "COINS":
            value = base_price * coin_bonus
        elif item in lbin_prices:
            value = lbin_prices[item]
        else:
            value = base_price

        ev += p * value

    return ev