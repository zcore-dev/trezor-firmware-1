# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class EosActionSellRam(p.MessageType):

    def __init__(
        self,
        account: int = None,
        bytes: int = None,
    ) -> None:
        self.account = account
        self.bytes = bytes

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('account', p.UVarintType, 0),
            2: ('bytes', p.UVarintType, 0),
        }
