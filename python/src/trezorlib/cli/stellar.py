import base64

import click

from .. import tools, stellar

PATH_HELP = "BIP32 path. Always use hardened paths and the m/44'/148'/ prefix"


@click.group(name="stellar")
def cli():
    """Stellar commands."""


@cli.command()
@click.option(
    "-n",
    "--address",
    required=False,
    help=PATH_HELP,
    default=stellar.DEFAULT_BIP32_PATH,
)
@click.option("-d", "--show-display", is_flag=True)
@click.pass_obj
def get_address(connect, address, show_display):
    """Get Stellar public address"""
    client = connect()
    address_n = tools.parse_path(address)
    return stellar.get_address(client, address_n, show_display)


@cli.command()
@click.option(
    "-n",
    "--address",
    required=False,
    help=PATH_HELP,
    default=stellar.DEFAULT_BIP32_PATH,
)
@click.option(
    "-n",
    "--network-passphrase",
    default=stellar.DEFAULT_NETWORK_PASSPHRASE,
    required=False,
    help="Network passphrase (blank for public network).",
)
@click.argument("b64envelope")
@click.pass_obj
def sign_transaction(connect, b64envelope, address, network_passphrase):
    """Sign a base64-encoded transaction envelope
    
    For testnet transactions, use the following network passphrase:
    'Test SDF Network ; September 2015'
    """
    client = connect()
    address_n = tools.parse_path(address)
    tx, operations = stellar.parse_transaction_bytes(base64.b64decode(b64envelope))
    resp = stellar.sign_tx(client, tx, operations, address_n, network_passphrase)

    return base64.b64encode(resp.signature)
