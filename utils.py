import pandas as pd
import requests

def fetch_recent_avg(item_ids):
    def avg_price(item):
        try:
            data = requests.get(
                f"https://sky.coflnet.com/api/auctions/tag/{item}/sold"
            ).json()

            auctions = data if isinstance(data, list) else data.get("auctions", [])

            prices = [
                a["startingBid"]
                for a in auctions[:10]
                if a.get("bin") and a.get("startingBid")
            ]

            return sum(prices) / len(prices) if prices else 0

        except:
            return 0

    return {item: avg_price(item) for item in item_ids}

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