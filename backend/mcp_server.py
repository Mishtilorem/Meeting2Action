from dotenv import load_dotenv
load_dotenv()
from mcp.server.fastmcp import FastMCP
from trello import create_card, update_card

mcp = FastMCP("meeting-tasks")

@mcp.tool()
def create_task(title: str, notes: str = "", due: str | None = None) -> str:
    """Create a task card on the Trello board and return its id."""
    return create_card(title, notes, due)

@mcp.tool()
def update_task(card_id: str, title: str, notes: str = "", due: str | None = None) -> str:
    """Update an existing Trello card's title, notes and due date."""
    return update_card(card_id, title, notes, due)

if __name__ == "__main__":
    mcp.run()

