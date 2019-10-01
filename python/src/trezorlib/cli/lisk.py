import json

import click

from .. import lisk, tools


PATH_HELP = "BIP-32 path, e.g. m/44'/134'/0'/0'"


@click.group(name="lisk")
def cli():
    """Lisk commands."""


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.option("-d", "--show-display", is_flag=True)
@click.pass_obj
def get_address(connect, address, show_display):
    """Get Lisk address for specified path."""
    client = connect()
    address_n = tools.parse_path(address)
    return lisk.get_address(client, address_n, show_display)


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.option("-d", "--show-display", is_flag=True)
@click.pass_obj
def get_public_key(connect, address, show_display):
    """Get Lisk public key for specified path."""
    client = connect()
    address_n = tools.parse_path(address)
    res = lisk.get_public_key(client, address_n, show_display)
    output = {"public_key": res.public_key.hex()}
    return output


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.option(
    "-f", "--file", type=click.File("r"), default="-", help="Transaction in JSON format"
)
# @click.option('-b', '--broadcast', help='Broadcast Lisk transaction')
@click.pass_obj
def sign_tx(connect, address, file):
    """Sign Lisk transaction."""
    client = connect()
    address_n = tools.parse_path(address)
    transaction = lisk.sign_tx(client, address_n, json.load(file))

    payload = {"signature": transaction.signature.hex()}

    return payload


@cli.command()
@click.option("-n", "--address", required=True, help=PATH_HELP)
@click.argument("message")
@click.pass_obj
def sign_message(connect, address, message):
    """Sign message with Lisk address."""
    client = connect()
    address_n = client.expand_path(address)
    res = lisk.sign_message(client, address_n, message)
    output = {
        "message": message,
        "public_key": res.public_key.hex(),
        "signature": res.signature.hex(),
    }
    return output


@cli.command()
@click.argument("pubkey")
@click.argument("signature")
@click.argument("message")
@click.pass_obj
def verify_message(connect, pubkey, signature, message):
    """Verify message signed with Lisk address."""
    signature = bytes.fromhex(signature)
    pubkey = bytes.fromhex(pubkey)
    return lisk.verify_message(connect(), pubkey, signature, message)
