from rich.console import Console
from rich.table import Table
from chess_rag.helpers.db_handler import DBHandler

class ListUsersHandler:
    def __init__(self) -> None:
        pass

    def list_users(self):
        db = DBHandler()
        users = db.get_users()
        console = Console()
        table = Table(title="Users")
        table.add_column("Username")
        table.add_column("Last Updated")
        for user in users:
            table.add_row(user[0], user[1])
        console.print(table)
