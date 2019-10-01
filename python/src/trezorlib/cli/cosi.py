import click

from .. import tools, cosi

PATH_HELP = "BIP-32 path, e.g. m/44'/0'/0'/0/0"


@click.group(name="cosi")
def cli():
    """CoSi (Cothority / collective signing) commands."""


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.argument("data")
@click.pass_obj
def commit(connect, address, data):
    """Ask device to commit to CoSi signing."""
    client = connect()
    address_n = tools.parse_path(address)
    return cosi.commit(client, address_n, bytes.fromhex(data))


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.argument("data")
@click.argument("global_commitment")
@click.argument("global_pubkey")
@click.pass_obj
def sign(connect, address, data, global_commitment, global_pubkey):
    """Ask device to sign using CoSi."""
    client = connect()
    address_n = tools.parse_path(address)
    return cosi.sign(
        client,
        address_n,
        bytes.fromhex(data),
        bytes.fromhex(global_commitment),
        bytes.fromhex(global_pubkey),
    )
