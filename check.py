import requests
import time

COMPOUND_API = "https://api.compound.finance/api/v2/account"
MAX_PAGES = 10000
PAGE_SIZE = 500
REQUERY_SLEEP_TIME = 1
MAX_REQUERY_SLEEP_TIME = 3

cTokenToToken = {
    '0x6c8c6b02e7b2be14d4fa6022dfd6d75921d90e4e': 'BAT',
    '0x39aa39c021dfbae8fac545936693ac917d5e7563': 'USDC',
    '0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5': 'ETH',
    '0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9': 'USDT',
    '0x5d3a536e4d6dbd6114cc1ead35777bab948e3643': 'DAI',
    '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4': 'WBTC',
    '0x158079ee67fce2f58472a96584a73c7ab9ac95c1': 'REP',
    '0xb3319f5d18bc0d84dd1b4825dcde5d5f7266d407': 'ZRX',
    '0xf5dce57282a584d2746faf1593d3121fcac444dc': 'SAI',
    }

tokenPrice = {
    'BAT': 0.25,
    'USDC': 1.0,
    'ETH': 227.0,
    'USDT': 1.0,
    'DAI': 1.01,
    'WBTC': 9147,
    'REP': 16.8,
    'ZRX': 0.336,
    'SAI': 1.20
}

tokenBorrowNet = {key: 0.0 for key in tokenPrice.keys()}
tokenSupplyNet = {key: 0.0 for key in tokenPrice.keys()}
tokenBorrowGross = {key: 0.0 for key in tokenPrice.keys()}
tokenSupplyGross = {key: 0.0 for key in tokenPrice.keys()}

prev_page_number = 0
sleep_time = REQUERY_SLEEP_TIME

for i in range(1, MAX_PAGES):
    while sleep_time < MAX_REQUERY_SLEEP_TIME:
        query = COMPOUND_API + f"?page_size={PAGE_SIZE}&page_number={i}"
        response = requests.get(query)
        if response.ok:
            sleep_time = REQUERY_SLEEP_TIME
            break
        else:
            print(f"{query} got error response: {response}, waiting for {sleep_time} seconds")
            time.sleep(sleep_time)
            sleep_time += 1
    else:
        print(f"Could not retrieve page {i}, skipping...")
        sleep_time = REQUERY_SLEEP_TIME
        continue

    j = response.json()
    if j["pagination_summary"]["page_number"] <= prev_page_number:
        break
    else:
        prev_page_number = j["pagination_summary"]["page_number"]
    for account in j["accounts"]:
        for cToken in account["tokens"]:
            if cToken['address'] not in cTokenToToken:
                continue
            token = cTokenToToken[cToken['address']]
            supply = float(cToken["supply_balance_underlying"]["value"])
            borrow = float(cToken["borrow_balance_underlying"]["value"])
            net = supply - borrow
            tokenSupplyGross[token] += supply
            tokenBorrowGross[token] += borrow
            if net > 0:
                tokenSupplyNet[token] += net
            elif net < 0:
                tokenBorrowNet[token] -= net

for token, price in tokenPrice.items():
    print(f"{token} net supply: ${tokenSupplyNet[token] * price:,.2f}")
    print(f"{token} net borrow: ${tokenBorrowNet[token] * price:,.2f}")
    print(f"{token} gross supply: ${tokenSupplyGross[token] * price:,.2f}")
    print(f"{token} gross borrow: ${tokenBorrowGross[token] * price:,.2f}")


print(f"Total net supply: ${sum([tokenSupplyNet[token] * price for (token, price) in tokenPrice.items()]):,.2f}")
print(f"Total net borrow: ${sum([tokenBorrowNet[token] * price for (token, price) in tokenPrice.items()]):,.2f}")

print(f"Total gross supply: ${sum([tokenSupplyGross[token] * price for (token, price) in tokenPrice.items()]):,.2f}")
print(f"Total gross borrow: ${sum([tokenBorrowGross[token] * price for (token, price) in tokenPrice.items()]):,.2f}")
