from requests import get, post
from json import load, dump

DATA_URL = "https://accounts.klei.com/account/transactions/data.json"
ROLLBACK_URL = "https://accounts.klei.com/account/transactions/rollback"

TYPE_WHITELIST = [
    "TXN_SPOOLS_FOR_ITEM",
    "TXN_ITEM_FOR_SPOOLS"
]

headers_file = {}
with open("headers.json", 'r', encoding="UTF-8") as file:
    headers_file = load(file)

secret = {}
with open("secret.json", 'r', encoding="UTF-8") as file:
    secret = load(file)

data_headers = headers_file["data"]
rollback_headers = headers_file["rollback"]
data_headers["Cookie"] = headers_file["session"] % secret["sessionCookie"]
rollback_headers["Cookie"] = headers_file["session"] % secret["sessionCookie"]
del headers_file

transactions = {}
data_file_response = get(DATA_URL, headers=data_headers)
del data_headers
data_file_response.raise_for_status()
transactions = data_file_response.json()["data"]["Transactions"]
del data_file_response


for transaction in transactions:
    if not transaction["Type"] in TYPE_WHITELIST or transaction["Time"] < secret["rollbackFrom"]:
        continue
    
    # Если всё прошло гладко
    rollback_data = {
        "csrfToken": secret["csrfToken"],
        "txnID": transaction["TxnID"],
        "game": secret["game"]
    }
    rollback_response = post(ROLLBACK_URL, data=rollback_data, headers=rollback_headers)
    del rollback_data
    rollback_response.raise_for_status()
    secret["csrfToken"] = rollback_response.json()["data"]["NewCSRFToken"]
    del rollback_response
    if transaction.has_key("ItemGains")
        item_type = transaction["ItemGains"][0]["Type"]
        print(f"Rollbacked item creation \"{item_type}\"")
        del item_type
    elif transaction.has_key("ItemLosses")
        item_type = transaction["ItemLosses"][0]["Type"]
        print(f"Rollbacked item destroying \"{item_type}\"")
        del item_type

with open("secret.json", 'w', encoding="UTF-8") as file:
    dump(secret, file, ensure_ascii=False, indent='\t')

print("\nDone!")