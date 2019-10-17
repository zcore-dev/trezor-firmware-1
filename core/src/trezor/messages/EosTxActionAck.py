# Automatically generated by pb2py
# fmt: off
import protobuf as p

from .EosActionBuyRam import EosActionBuyRam
from .EosActionBuyRamBytes import EosActionBuyRamBytes
from .EosActionCommon import EosActionCommon
from .EosActionDelegate import EosActionDelegate
from .EosActionDeleteAuth import EosActionDeleteAuth
from .EosActionLinkAuth import EosActionLinkAuth
from .EosActionNewAccount import EosActionNewAccount
from .EosActionRefund import EosActionRefund
from .EosActionSellRam import EosActionSellRam
from .EosActionTransfer import EosActionTransfer
from .EosActionUndelegate import EosActionUndelegate
from .EosActionUnknown import EosActionUnknown
from .EosActionUnlinkAuth import EosActionUnlinkAuth
from .EosActionUpdateAuth import EosActionUpdateAuth
from .EosActionVoteProducer import EosActionVoteProducer

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class EosTxActionAck(p.MessageType):
    MESSAGE_WIRE_TYPE = 604

    def __init__(
        self,
        common: EosActionCommon = None,
        transfer: EosActionTransfer = None,
        delegate: EosActionDelegate = None,
        undelegate: EosActionUndelegate = None,
        refund: EosActionRefund = None,
        buy_ram: EosActionBuyRam = None,
        buy_ram_bytes: EosActionBuyRamBytes = None,
        sell_ram: EosActionSellRam = None,
        vote_producer: EosActionVoteProducer = None,
        update_auth: EosActionUpdateAuth = None,
        delete_auth: EosActionDeleteAuth = None,
        link_auth: EosActionLinkAuth = None,
        unlink_auth: EosActionUnlinkAuth = None,
        new_account: EosActionNewAccount = None,
        unknown: EosActionUnknown = None,
    ) -> None:
        self.common = common
        self.transfer = transfer
        self.delegate = delegate
        self.undelegate = undelegate
        self.refund = refund
        self.buy_ram = buy_ram
        self.buy_ram_bytes = buy_ram_bytes
        self.sell_ram = sell_ram
        self.vote_producer = vote_producer
        self.update_auth = update_auth
        self.delete_auth = delete_auth
        self.link_auth = link_auth
        self.unlink_auth = unlink_auth
        self.new_account = new_account
        self.unknown = unknown

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('common', EosActionCommon, 0),
            2: ('transfer', EosActionTransfer, 0),
            3: ('delegate', EosActionDelegate, 0),
            4: ('undelegate', EosActionUndelegate, 0),
            5: ('refund', EosActionRefund, 0),
            6: ('buy_ram', EosActionBuyRam, 0),
            7: ('buy_ram_bytes', EosActionBuyRamBytes, 0),
            8: ('sell_ram', EosActionSellRam, 0),
            9: ('vote_producer', EosActionVoteProducer, 0),
            10: ('update_auth', EosActionUpdateAuth, 0),
            11: ('delete_auth', EosActionDeleteAuth, 0),
            12: ('link_auth', EosActionLinkAuth, 0),
            13: ('unlink_auth', EosActionUnlinkAuth, 0),
            14: ('new_account', EosActionNewAccount, 0),
            15: ('unknown', EosActionUnknown, 0),
        }
