import os
import httpx

def create_card(title, desc="", due=None):
    if os.getenv("DRY_RUN") == "1":
        return "dry-run"
    params = {
        "key": os.environ["TRELLO_KEY"],
        "token": os.environ["TRELLO_TOKEN"],
        "idList": os.environ["TRELLO_LIST_ID"],
        "name": title,
        "desc": desc,
    }
    if due:
        params["due"] = due
    r = httpx.post("https://api.trello.com/1/cards", params=params, timeout=20)
    r.raise_for_status()
    return r.json()["id"]
