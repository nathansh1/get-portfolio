import requests
import json
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
USER_ADDRESS = input("Enter user Solana address: ").strip()

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
tokens = [token for token in response.get("items") if token.get("interface") == "FungibleToken"]

with open("response.json", "w") as file:
    json.dump(response, file, indent=4)

with open("tokens.json", "w") as file:
    json.dump(tokens, file, indent=4)

if "error" in response:
    print("API Error:", response["error"]["message"])
else:
    usd_value = response.get("nativeBalance").get("total_price")
    sol_price = response.get("nativeBalance").get("price_per_sol")

    print("\n")
    print(f"Portfolio Value (USD): {usd_value}")
    print(f"Portfolio Value (SOL): {usd_value / sol_price}")
    print("\n")

    token_table = [
        ["Token", "Balance", "Price", "Value"]
    ]

    for token in tokens:
        row = []
        token_info = token.get("token_info")
        price_info = token_info.get("price_info")

        if price_info is None:
            continue

        row.append(token_info.get("symbol").capitalize())
        balance = token_info.get("balance")
        row.append(f"{balance:,}")

        price = price_info.get("price_per_token")
        row.append("$" + str(price))

        value = price_info.get("total_price")

        # Round value to 2 decimal places, format with commas
        row.append("$" + f"{value:,.2f}")

        if None in row:
            continue
        
        token_table.append(row)

    print(tabulate(token_table[1:], headers = token_table[0], tablefmt = "simple"))