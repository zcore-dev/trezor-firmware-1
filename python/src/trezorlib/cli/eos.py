import json

import click

from .. import tools, eos

PATH_HELP = "BIP-32 path, e.g. m/44'/194'/0'/0/0"


@click.group(name="eos")
def cli():
    """EOS commands."""


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.option("-d", "--show-display", is_flag=True)
@click.pass_obj
def get_public_key(connect, address, show_display):
    """Get Eos public key in base58 encoding."""
    client = connect()
    address_n = tools.parse_path(address)
    res = eos.get_public_key(client, address_n, show_display)
    return "WIF: {}\nRaw: {}".format(res.wif_public_key, res.raw_public_key.hex())


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    required=True,
    help="Transaction in JSON format",
)
@click.pass_obj
def sign_transaction(connect, address, file):
    """Sign EOS transaction."""
    client = connect()

    tx_json = json.load(file)

    address_n = tools.parse_path(address)
    return eos.sign_tx(client, address_n, tx_json["transaction"], tx_json["chain_id"])
