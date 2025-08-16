```import pandas as pd
import requests
import time
from datetime import datetime, timezone, timedelta

now = datetime.fromtimestamp(time.time(), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
bazaar = {
    k: {
        "Sell": v["quick_status"]["sellPrice"],
        "Buy": v["quick_status"]["buyPrice"]
    }
    for k, v in requests.get("https://api.hypixel.net/v2/skyblock/bazaar").json()['products'].items()
}
gg = requests.get('https://sky.coflnet.com/api/auctions/tag/GOLD_GIFT/active/bin').json()[0]['startingBid']
ggt = requests.get('https://sky.coflnet.com/api/auctions/tag/GOLD_GIFT_TALISMAN/active/bin').json()[0]['startingBid']
snow = requests.get('https://sky.coflnet.com/api/auctions/tag/PET_SNOWMAN/active/bin').json()[0]['startingBid']
cryo = (lambda d: d[0].get('startingBid', 0) if d else 0)(
    requests.get('https://sky.coflnet.com/api/auctions/tag/SNOW_HOWITZER/active/bin').json()
)
kram = requests.get('https://sky.coflnet.com/api/auctions/tag/KRAMPUS_HELMET/active/bin').json()[0]['startingBid']

buff = 1.35 #Gold gift talisman and snowman mask (BOTH PLAYERS)

north_stars = round((ggt - gg) / 420)

profit = {
    "Red": {"Gift": {"Buy": 0,"Sell":0}, "Stars": 0},
    "Green": {"Gift": {"Buy": 0,"Sell":0}, "Stars": 0},
    "White": {"Gift": {"Buy": 0,"Sell":0}, "Stars": 0},
}

with open('red.csv','r') as f:
    red = pd.read_csv(f)
    red['Price'] *= buff
    red.loc[red['Item'] == 'GOLD_GIFT', 'Price'] = gg
    red.loc[red['Item'] == 'Snow', 'Price'] = snow
    red.loc[red['Item'] == 'Cryo', 'Price'] = cryo
    red.loc[red['Item'] == 'Kram', 'Price'] = kram
    red['Per Gift'] = red['Weight'] / sum(red['Weight']) * red['Price']
    profit['Red']['Gift']['Buy'] = round(2*sum(red['Per Gift']) - bazaar['RED_GIFT']['Buy'])
    profit['Red']['Gift']['Sell'] = round(2*sum(red['Per Gift']) - bazaar['RED_GIFT']['Sell']) 
    profit['Red']['Stars'] = 3 * north_stars
    red['Chance'] = red['Weight'] / sum(red['Weight'])

with open('green.csv','r') as f:
    green = pd.read_csv(f)
    green['Price'] *= buff
    green.loc[green['Item'] == 'GOLD_GIFT', 'Price'] = gg
    green['Per Gift'] = green['Weight'] / sum(green['Weight']) * green['Price']
    profit['Green']['Gift']['Buy'] = round(2*sum(green['Per Gift']) - bazaar['GREEN_GIFT']['Buy'])
    profit['Green']['Gift']['Sell'] = round(2*sum(green['Per Gift']) - bazaar['GREEN_GIFT']['Sell']) 
    profit['Green']['Stars'] = 1.2 * north_stars

with open('white.csv','r') as f:
    white = pd.read_csv(f)
    white['Price'] *= buff
    white['Per Gift'] = white['Weight'] / sum(white['Weight']) * white['Price']
    profit['White']['Gift']['Buy'] = round(2*sum(white['Per Gift']) - bazaar['WHITE_GIFT']['Buy'])
    profit['White']['Gift']['Sell'] = round(2*sum(white['Per Gift']) - bazaar['WHITE_GIFT']['Sell'])
    profit['White']['Stars'] = 0.2 * north_stars

print(f"Red: {profit['Red']['Gift']}, max cost: {profit['Red']['Gift']['Sell'] + bazaar['RED_GIFT']['Sell']}")
print(f"Green: {(profit['Green']['Gift'])}, max cost: {profit['Green']['Gift']['Sell'] + bazaar['GREEN_GIFT']['Sell']}")
print(f"White: {profit['White']['Gift']}, max cost: {profit['White']['Gift']['Sell'] + bazaar['WHITE_GIFT']['Sell']}")```
