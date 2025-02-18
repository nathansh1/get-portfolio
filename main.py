import requests
import json
import os
from dotenv import load_dotenv
from tabulate import tabulate
import sys
import re

load_dotenv()

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
USER_ADDRESS = input("\n\nEnter Solana address: ").strip()

response = requests.post(
    f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}",
    headers = {"Content-Type": "application/json"},
    json={
        "id": "text",
        "jsonrpc": "2.0",
        "method": "getAssetsByOwner",
        "params": {
            "ownerAddress": USER_ADDRESS,
            "page": 1,
            "limit": 100,
            "options": {
                "showUnverifiedCollections": False,
                "showCollectionMetadata": False,
                "showGrandTotal": False,
                "showFungible": True,
                "showNativeBalance": True,
                "showInscription": False,
                "showZeroBalance": False
            },
            "sortBy": {
                "sortBy": "created",
                "sortDirection": "asc"
            }
        }
    }
)

response = response.json().get("result")

if response is None:
    print("Bad address")
    sys.exit(1)


tokens = [token for token in response.get("items") if token.get("interface") == "FungibleToken"]

with open("response.json", "w") as file:
    json.dump(response, file, indent=4)

with open("tokens.json", "w") as file:
    json.dump(tokens, file, indent=4)

if "error" in response:
    print("API Error:", response["error"]["message"])
    sys.exit(1)

native_balance = response.get("nativeBalance")
sol_value = native_balance.get("total_price")
sol_price = native_balance.get("price_per_sol")

token_table = [
    ["Token", "Balance", "Price", "Value"]
]

sol_balance = native_balance.get("lamports") / 1000000000

row = ["SOL", f"{sol_balance:,}", f"${sol_price:,.2f}", f"${sol_value:,.2f}"]
token_table.append(row)

total_usd_value = sol_value

for token in tokens:
    row = []
    token_info = token.get("token_info")
    price_info = token_info.get("price_info")

    if price_info is None:
        continue

    row.append(token_info.get("symbol").upper())

    balance = token_info.get("balance")
    row.append(f"{balance:,}")

    price = price_info.get("price_per_token")
    if price >= 1:
        row.append(f"${price:,.2f}")
    else:
        row.append("$" + str(price))

    value = price_info.get("total_price")
    total_usd_value += value

    formatted_value = f"${value:,.2f}"

    row.append(f"${value:,.2f}")

    if None in row:
        continue
    
    for i in range(2, len(token_table)):
        if (float(token_table[i][3].replace(",", "").replace("$", "")) < value):
            token_table.insert(i, row)
            break

    if row not in token_table:
        token_table.append(row)

print("\n")
print(f"Portfolio Value (USD): ${total_usd_value:,.2f}")
print(f"Portfolio Value (SOL): {total_usd_value / sol_price:,.4f}")
print("\n")

token_table.insert(2, [])
print(tabulate(token_table[1:], headers = token_table[0], tablefmt = "simple"))