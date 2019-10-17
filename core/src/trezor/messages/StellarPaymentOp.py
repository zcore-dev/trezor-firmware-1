# Automatically generated by pb2py
# fmt: off
import protobuf as p

from .StellarAssetType import StellarAssetType

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class StellarPaymentOp(p.MessageType):
    MESSAGE_WIRE_TYPE = 211

    def __init__(
        self,
        source_account: str = None,
        destination_account: str = None,
        asset: StellarAssetType = None,
        amount: int = None,
    ) -> None:
        self.source_account = source_account
        self.destination_account = destination_account
        self.asset = asset
        self.amount = amount

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('source_account', p.UnicodeType, 0),
            2: ('destination_account', p.UnicodeType, 0),
            3: ('asset', StellarAssetType, 0),
            4: ('amount', p.SVarintType, 0),
        }
