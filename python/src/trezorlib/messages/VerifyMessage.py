# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class VerifyMessage(p.MessageType):
    MESSAGE_WIRE_TYPE = 39

    def __init__(
        self,
        address: str = None,
        signature: bytes = None,
        message: bytes = None,
        coin_name: str = None,
    ) -> None:
        self.address = address
        self.signature = signature
        self.message = message
        self.coin_name = coin_name

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('address', p.UnicodeType, 0),
            2: ('signature', p.BytesType, 0),
            3: ('message', p.BytesType, 0),
            4: ('coin_name', p.UnicodeType, 0),  # default=Bitcoin
        }
