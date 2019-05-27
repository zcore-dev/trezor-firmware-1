# Binance format serializer
#
# Encoding Documentation:
# https://binance-chain.github.io/encoding.html#binance-chain-transaction-encoding-specification
#

from ubinascii import unhexlify

from trezor.messages.BinanceCancelMsg import BinanceCancelMsg
from trezor.messages.BinanceOrderMsg import BinanceOrderMsg
from trezor.messages.BinanceSignTx import BinanceSignTx
from trezor.messages.BinanceTransferMsg import BinanceTransferMsg

from .helpers import encode_binary_address, encode_binary_amount

# message prefixes
STANDARD_TX_PREFIX = unhexlify("F0625DEE")
PUBKEY_PREFIX = unhexlify("EB5AE987")
SEND_MSG_PREFIX = unhexlify("2A2C87FA")
NEW_ORDER_MSG_PREFIX = unhexlify("CE6DC043")
CANCEL_ORDER_MSG_PREFIX = unhexlify("166E681B")
FREEZE_TOKEN_MSG_PREFIX = unhexlify("E774B32D")
UNFREEZE_TOKEN_MSG_PREFIX = unhexlify("6515FF0D")
VOTE_MSG_PREFIX = unhexlify("A1CADD36")

# KEY PREFIXES TODO: make this simple

# key prefixes for signature message
SIGNATURE_KEY_PREFIX = 0x12
ACCOUNT_NUMBER_KEY_PREFIX = 0x18
SEQUENCE_KEY_PREFIX = 0x20

# key prefixes for new order message
NEWORDER_SENDER_KEY_PREFIX = 0x0A
NEWORDER_ID_KEY_PREFIX = 0x12
NEWORDER_SYMBOL_KEY_PREFIX = 0x1A
NEWORDER_ORDERTYPE_KEY_PREFIX = 0x20
NEWORDER_SIDE_KEY_PREFIX = 0x28
NEWORDER_PRICE_KEY_PREFIX = 0x30
NEWORDER_QUANTITY_KEY_PREFIX = 0x38
NEWORDER_TIMEINFORCE_KEY_PREFIX = 0x40

# key prefixes for cancel message
CANCEL_SENDER_KEY_PREFIX = 0x0A
CANCEL_SYMBOL_KEY_PREFIX = 0x12
CANCEL_REFID_KEY_PREFIX = 0x1A

# key prefixes for send/transfer message
SEND_INPUTS_KEY_PREFIX = 0x0A
SEND_OUTPUTS_KEY_PREFIX = 0x12
SEND_COINS_KEY_PREFIX = 0x12
SEND_DENOM_KEY_PREFIX = 0x0A
SEND_AMOUNT_KEY_PREFIX = 0x10
SEND_ADDRESS_KEY_PREFIX = 0x0A

# key prefixes for standard transaction message
STDTX_NEW_ORDER_KEY_PREFIX = 0x0A
STDTX_PUBKEY_KEY_PREFIX = 0x0A
STDTX_STANDARD_TX_KEY_PREFIX = 0x01
STDTX_MEMO_KEY_PREFIX = 0x1A


# TODO: pass signature+pubkey or calculate them in serializer?
def encode(envelope: BinanceSignTx, msg, signature, pubkey):

    final_array = bytearray()
    final_array.extend(encode_object(msg))
    final_array.extend(encode_std_signature(envelope, signature, pubkey))

    if envelope.memo is not None and envelope.memo != "":
        final_array.append(STDTX_MEMO_KEY_PREFIX)
        final_array.extend(calculate_varint(len(envelope.memo)))
        final_array.extend(envelope.memo)

    final_array.append(0x20)
    final_array.append(envelope.source)

    final_array[0:0] = bytearray([len(final_array)])
    final_array[1:1] = unhexlify("01")

    return final_array


def encode_object(msg):
    w = bytearray()
    if isinstance(msg, BinanceTransferMsg):
        w = encode_transfer_msg(msg)
    elif isinstance(msg, BinanceOrderMsg):
        w = encode_order_msg(msg)
    elif isinstance(msg, BinanceCancelMsg):
        w = encode_cancel_msg(msg)
    else:
        raise ValueError("input message unrecognized, is of type " + type(msg).__name__)

    return w


def encode_order_msg(msg: BinanceOrderMsg):
    message_array = bytearray()
    message_array.extend(NEW_ORDER_MSG_PREFIX)

    message_array.append(NEWORDER_SENDER_KEY_PREFIX)
    sender = encode_binary_address(msg.sender)
    message_array.extend(calculate_varint(len(sender)))
    message_array.extend(sender)

    message_array.append(NEWORDER_ID_KEY_PREFIX)
    message_array.extend(calculate_varint(len(msg.id)))
    message_array.extend(msg.id)

    message_array.append(NEWORDER_SYMBOL_KEY_PREFIX)
    message_array.extend(calculate_varint(len(msg.symbol)))
    message_array.extend(msg.symbol)

    message_array.append(NEWORDER_ORDERTYPE_KEY_PREFIX)
    message_array.append(msg.ordertype)

    message_array.append(NEWORDER_SIDE_KEY_PREFIX)
    message_array.append(msg.side)

    message_array.append(NEWORDER_PRICE_KEY_PREFIX)
    message_array.extend(encode_binary_amount(msg.price))

    message_array.append(NEWORDER_QUANTITY_KEY_PREFIX)
    message_array.extend(encode_binary_amount(msg.quantity))

    message_array.append(NEWORDER_TIMEINFORCE_KEY_PREFIX)
    message_array.append(msg.timeinforce)

    array_length = calculate_varint(len(message_array))

    message_array[0:0] = STANDARD_TX_PREFIX
    message_array[4:4] = unhexlify("0A")  # TODO: replace with const
    message_array[5:5] = array_length

    return message_array


def encode_std_signature(msg: BinanceSignTx, signature, pubkey):
    pubkey_size = calculate_varint(len(pubkey))
    pubkey_array = bytearray()
    pubkey_array.extend(PUBKEY_PREFIX)
    pubkey_array.extend(pubkey_size)
    pubkey_array.extend(pubkey)

    pubkey_array[0:0] = calculate_varint(len(pubkey_array))
    pubkey_array[0:0] = unhexlify("0A")  # TODO: replace with const

    pubkey_array.append(SIGNATURE_KEY_PREFIX)
    pubkey_array.extend(calculate_varint(len(signature)))
    pubkey_array.extend(signature)
    pubkey_array.append(ACCOUNT_NUMBER_KEY_PREFIX)
    pubkey_array.append(msg.account_number)
    pubkey_array.append(SEQUENCE_KEY_PREFIX)
    pubkey_array.append(msg.sequence)

    pubkey_array[0:0] = calculate_varint(len(pubkey_array))
    pubkey_array[0:0] = unhexlify("12")  # TODO: replace with const

    return pubkey_array


def encode_cancel_msg(msg: BinanceCancelMsg):
    w = bytearray()
    w.extend(CANCEL_ORDER_MSG_PREFIX)
    w.append(CANCEL_SENDER_KEY_PREFIX)
    sender = encode_binary_address(msg.sender)
    w.extend(calculate_varint(len(sender)))
    w.extend(sender)
    w.append(CANCEL_SYMBOL_KEY_PREFIX)
    w.extend(calculate_varint(len(msg.symbol)))
    w.extend(msg.symbol)
    w.append(CANCEL_REFID_KEY_PREFIX)
    w.extend(calculate_varint(len(msg.refid)))
    w.extend(msg.refid)

    array_length = calculate_varint(len(w))

    w[0:0] = STANDARD_TX_PREFIX
    w[4:4] = unhexlify("0A")  # TODO: replace with const
    w[5:5] = array_length

    return w


def encode_transfer_msg(msg: BinanceTransferMsg):
    w = bytearray()
    w.extend(SEND_MSG_PREFIX)

    for txinput in msg.inputs:
        input_address = encode_binary_address(txinput.address)
        inputs = bytearray()
        inputs.append(SEND_ADDRESS_KEY_PREFIX)
        inputs.extend(calculate_varint(len(input_address)))
        inputs.extend(input_address)

        for coin in txinput.coins:
            input_coins = bytearray()
            input_coins.append(SEND_DENOM_KEY_PREFIX)
            input_coins.extend(calculate_varint(len(coin.denom)))
            input_coins.extend(coin.denom)
            input_coins.append(SEND_AMOUNT_KEY_PREFIX)
            input_amount = encode_binary_amount(coin.amount)
            input_coins.extend(input_amount)
            inputs.append(0x12)  # TODO: replace with const
            inputs.extend(calculate_varint(len(input_coins)))
            inputs.extend(input_coins)

        w.append(SEND_INPUTS_KEY_PREFIX)
        w.extend(calculate_varint(len(inputs)))
        w.extend(inputs)

    for txoutput in msg.outputs:
        output_address = encode_binary_address(txoutput.address)

        outputs = bytearray()
        outputs.append(SEND_ADDRESS_KEY_PREFIX)
        outputs.extend(calculate_varint(len(output_address)))
        outputs.extend(output_address)

        for coin in txoutput.coins:
            output_coins = bytearray()
            output_coins.append(SEND_DENOM_KEY_PREFIX)
            output_coins.extend(calculate_varint(len(coin.denom)))
            output_coins.extend(coin.denom)
            output_coins.append(SEND_AMOUNT_KEY_PREFIX)
            output_coins.extend(encode_binary_amount(coin.amount))
            outputs.append(0x12)  # TODO: replace with const
            outputs.extend(calculate_varint(len(output_coins)))
            outputs.extend(output_coins)

        w.append(SEND_OUTPUTS_KEY_PREFIX)
        w.extend(calculate_varint(len(outputs)))
        w.extend(outputs)

    array_length = calculate_varint(len(w))

    w[0:0] = STANDARD_TX_PREFIX
    w[4:4] = unhexlify("0A")  # TODO: replace with const
    w[5:5] = array_length

    return w


# TODO - this is used from ripple, use the ripple implementation?
def calculate_varint(val: int):
    w = bytearray()
    if val < 0:
        raise ValueError("Only non-negative integers are supported")
    elif val < 192:
        w.append(val)
    elif val <= 12480:
        val -= 193
        w.append(193 + rshift(val, 8))
        w.append(val & 0xFF)
    elif val <= 918744:
        val -= 12481
        w.append(241 + rshift(val, 16))
        w.append(rshift(val, 8) & 0xFF)
        w.append(val & 0xFF)
    else:
        raise ValueError("Value is too large")

    return w


def rshift(val, n):
    """
    Implements signed right-shift.
    See: http://stackoverflow.com/a/5833119/15677
    """
    return (val % 0x100000000) >> n
