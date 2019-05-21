from binascii import hexlify
from typing import List

from . import messages
from .tools import expect, session

@expect(messages.BinanceAddress, field="address")
def get_address(client, address_n, show_display=False):
    return client.call(
        messages.BinanceGetAddress(address_n=address_n, show_display=show_display)
    )

@expect(messages.BinancePublicKey, field="public_key")
def get_public_key(client, address_n, show_display=False):
    return client.call(
        messages.BinanceGetPublicKey(address_n=address_n, show_display=show_display)
    )

#TODO: implement all messages exchange
@session
def sign_tx(client, address_n, msg: messages.BinanceSignTx):
    msg.address = address_n
    return client.call(msg)

def create_sign_tx_msg(transaction) -> messages.BinanceSignTx:
    return messages.BinanceSignTx