import click


@click.group()
def cli():
    """
    checkmate
    """
    pass

@cli.command(name='add')
@click.argument('username', required=True)
def add(username): 
    from .helpers.add_user_handler import AddUserHandler

    add_handler = AddUserHandler(username=username)
    add_handler.run()