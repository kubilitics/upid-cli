import click
from upid.commands.cloud import cloud as cloud_group

@click.group()
def cli():
    pass

cli.add_command(cloud_group, name='cloud')

if __name__ == '__main__':
    cli() 