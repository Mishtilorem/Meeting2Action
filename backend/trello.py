import os
import httpx

def build_notes(owner, quote):
    return f"Owner: {owner or 'unassigned'}\nSource: \"{quote}\""

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

def update_card(card_id, title, desc="", due=None):
    if card_id == "dry-run" or os.getenv("DRY_RUN") == "1":
        return card_id
    params = {
        "key": os.environ["TRELLO_KEY"],
        "token": os.environ["TRELLO_TOKEN"],
        "name": title,
        "desc": desc,
        "due": due if due else "null",
    }
    r = httpx.put(f"https://api.trello.com/1/cards/{card_id}", params=params, timeout=20)
    r.raise_for_status()
    return card_id

