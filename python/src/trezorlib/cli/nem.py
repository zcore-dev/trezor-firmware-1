import json

import click
import requests

from .. import tools, nem

PATH_HELP = "BIP-32 path, e.g. m/44'/134'/0'/0'"


@click.group(name="nem")
def cli():
    """NEM commands."""


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.option("-N", "--network", type=int, default=0x68)
@click.option("-d", "--show-display", is_flag=True)
@click.pass_obj
def get_address(connect, address, network, show_display):
    """Get NEM address for specified path."""
    client = connect()
    address_n = tools.parse_path(address)
    return nem.get_address(client, address_n, network, show_display)


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    default="-",
    help="Transaction in NIS (RequestPrepareAnnounce) format",
)
@click.option("-b", "--broadcast", help="NIS to announce transaction to")
@click.pass_obj
def sign_tx(connect, address, file, broadcast):
    """Sign (and optionally broadcast) NEM transaction."""
    client = connect()
    address_n = tools.parse_path(address)
    transaction = nem.sign_tx(client, address_n, json.load(file))

    payload = {"data": transaction.data.hex(), "signature": transaction.signature.hex()}

    if broadcast:
        return requests.post(
            "{}/transaction/announce".format(broadcast), json=payload
        ).json()
    else:
        return payload
