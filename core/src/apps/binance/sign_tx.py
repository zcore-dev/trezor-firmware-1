from ubinascii import hexlify

from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import sha256
from trezor.messages import MessageType
from trezor.messages.BinanceSignedTx import BinanceSignedTx
from trezor.messages.BinanceSignTx import BinanceSignTx

from apps.binance import CURVE, helpers, layout
from apps.binance.serialize import encode
from apps.common import paths


async def sign_tx(ctx, envelope: BinanceSignTx, msg, keychain):
    # create transaction message -> sign it -> create signature/pubkey message -> serialize all

    await paths.validate_path(
        ctx, helpers.validate_full_path, keychain, envelope.address_n, CURVE
    )

    node = keychain.derive(envelope.address_n)

    msg_json = helpers.produce_json_for_signing(envelope, msg)
    signature_bytes = generate_content_signature(msg_json.encode(), node.private_key())
    encoded_message = encode(envelope, msg, signature_bytes, node.public_key())

    # TODO: what to validate/confirm with various messages?
    if msg.MESSAGE_WIRE_TYPE == MessageType.BinanceTransferMsg:
        for output in msg.outputs:
            for coin in output.coins:
                await layout.require_confirm_transfer(
                    ctx, hexlify(output.address), coin.amount, coin.denom
                )
    elif msg.MESSAGE_WIRE_TYPE == MessageType.BinanceOrderMsg:
        await layout.require_confirm_order(ctx)
    elif msg.MESSAGE_WIRE_TYPE == MessageType.BinanceCancelMsg:
        await layout.require_confirm_cancel(ctx)
    else:
        raise ValueError("input message unrecognized, is of type " + type(msg).__name__)

    return BinanceSignedTx(signature_bytes, node.public_key(), encoded_message)


def generate_content_signature(json: bytes, private_key: bytes) -> bytes:
    msghash = sha256(json).digest()
    return secp256k1.sign(private_key, msghash)[
        1:65
    ]  # TODO: FIGURE OUT WHY THE EXTRA FIRST BYTE!


def verify_content_signature(
    public_key: bytes, signature: bytes, unsigned_data: bytes
) -> bool:
    msghash = sha256(unsigned_data).digest()
    return secp256k1.verify(public_key, signature, msghash)
