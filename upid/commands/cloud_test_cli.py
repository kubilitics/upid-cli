import click
from upid.commands.cloud import cloud

@click.group()
def testcli():
    pass

testcli.add_command(cloud)

if __name__ == '__main__':
    testcli() 