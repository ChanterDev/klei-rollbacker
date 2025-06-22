from requests import get, post
from json import load, dump
from lxml.html import fromstring

HTML_URL = "https://accounts.klei.com/account/transactions"
DATA_URL = HTML_URL + "/data.json"
ROLLBACK_URL = HTML_URL + "/rollback"

TYPE_WHITELIST = [
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
html_headers = headers_file["html"]
data_headers["Cookie"] = headers_file["session"] % secret["sessionCookie"]
rollback_headers["Cookie"] = headers_file["session"] % secret["sessionCookie"]
html_headers["Cookie"] = headers_file["session"] % secret["sessionCookie"]
del headers_file

transactions = {}
data_file_response = get(DATA_URL, headers=data_headers)
del data_headers
data_file_response.raise_for_status()
transactions = data_file_response.json()["data"]["Transactions"]
del data_file_response

def get_csrf_from_html(content: str) -> str:
    root = fromstring(content)
    target = root.find(".//*[@id='csrfToken']")
    return target.get("value")

html_response = get(HTML_URL, headers=html_headers)
html_response.raise_for_status()
del html_headers
csrfToken = get_csrf_from_html(html_response.text)
del html_response

for transaction in transactions:
    if not transaction["Type"] in TYPE_WHITELIST or transaction["Time"] < secret["rollbackFrom"]:
        continue
    if transaction["ItemLosses"] != None:
        continue
    
    # Если всё прошло гладко
    rollback_data = {
        "csrfToken": csrfToken,
        "txnID": transaction["TxnID"],
        "game": secret["game"]
    }
    rollback_response = post(ROLLBACK_URL, data=rollback_data, headers=rollback_headers)
    del rollback_data
    rollback_response.raise_for_status()
    rollback_json = rollback_response.json()
    if not rollback_json["ok"]:
        error = rollback_json["error"]
        print(f"Klei status error: {error}")
        del error
        continue
    csrfToken = rollback_json["data"]["NewCSRFToken"]
    del rollback_json
    del rollback_response
    
    item_type = transaction["ItemLosses"][0]["Type"]
    print(f"Rollbacked item destroying \"{item_type}\"")
    del item_type

print("\nDone!")