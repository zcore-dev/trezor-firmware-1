# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

from .StellarAssetType import StellarAssetType

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class StellarPathPaymentOp(p.MessageType):
    MESSAGE_WIRE_TYPE = 212

    def __init__(
        self,
        source_account: str = None,
        send_asset: StellarAssetType = None,
        send_max: int = None,
        destination_account: str = None,
        destination_asset: StellarAssetType = None,
        destination_amount: int = None,
        paths: List[StellarAssetType] = None,
    ) -> None:
        self.source_account = source_account
        self.send_asset = send_asset
        self.send_max = send_max
        self.destination_account = destination_account
        self.destination_asset = destination_asset
        self.destination_amount = destination_amount
        self.paths = paths if paths is not None else []

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('source_account', p.UnicodeType, 0),
            2: ('send_asset', StellarAssetType, 0),
            3: ('send_max', p.SVarintType, 0),
            4: ('destination_account', p.UnicodeType, 0),
            5: ('destination_asset', StellarAssetType, 0),
            6: ('destination_amount', p.SVarintType, 0),
            7: ('paths', StellarAssetType, p.FLAG_REPEATED),
        }
