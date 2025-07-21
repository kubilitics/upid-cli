import click
from upid.commands.auth_universal import auth
from upid.commands.configurable_auth import configurable_auth
from upid.commands.onboarding import onboarding
from upid.commands.cluster import cluster
from upid.commands.analyze import analyze
from upid.commands.optimize import optimize
from upid.commands.deploy import deploy
from upid.commands.report import report
from upid.commands.universal import universal
from upid.commands.billing import billing
from upid.commands.intelligence import intelligence
from upid.commands.storage import storage
from upid.commands.cloud import cloud

@click.group()
def cli():
    pass

cli.add_command(auth)
cli.add_command(configurable_auth)
cli.add_command(onboarding)
cli.add_command(cluster)
cli.add_command(analyze)
cli.add_command(optimize)
cli.add_command(deploy)
cli.add_command(report)
cli.add_command(universal)
cli.add_command(billing)
cli.add_command(intelligence)
cli.add_command(storage)
cli.add_command(cloud, name='cloud')

if __name__ == '__main__':
    cli() 