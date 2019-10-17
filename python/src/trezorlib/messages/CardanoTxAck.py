# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class CardanoTxAck(p.MessageType):
    MESSAGE_WIRE_TYPE = 309

    def __init__(
        self,
        transaction: bytes = None,
    ) -> None:
        self.transaction = transaction

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('transaction', p.BytesType, 0),
        }
