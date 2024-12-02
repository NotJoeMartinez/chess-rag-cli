import click

from .helpers.add_user_handler import AddUserHandler
from .helpers.list_users_handler import ListUsersHandler

@click.group()
def cli():
    """
    Checkmate
    """
    pass

@cli.command(name='add')
@click.argument('username', required=True)
def add(username): 

    add_handler = AddUserHandler(username=username)
    add_handler.run()

@cli.command(name='list')
def list():
    list_handler = ListUsersHandler()
    list_handler.list_users()