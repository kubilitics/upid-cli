import click
from upid.commands.cloud import cloud

@click.group()
def cli():
    pass

cli.add_command(cloud)

if __name__ == '__main__':
    cli() 