# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class FirmwareUpload(p.MessageType):
    MESSAGE_WIRE_TYPE = 7

    def __init__(
        self,
        payload: bytes = None,
        hash: bytes = None,
    ) -> None:
        self.payload = payload
        self.hash = hash

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('payload', p.BytesType, 0),  # required
            2: ('hash', p.BytesType, 0),
        }
