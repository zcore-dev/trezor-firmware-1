# Automatically generated by pb2py
# fmt: off
import protobuf as p

from .MoneroExportedKeyImage import MoneroExportedKeyImage

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class MoneroKeyImageSyncStepAck(p.MessageType):
    MESSAGE_WIRE_TYPE = 533

    def __init__(
        self,
        kis: List[MoneroExportedKeyImage] = None,
    ) -> None:
        self.kis = kis if kis is not None else []

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('kis', MoneroExportedKeyImage, p.FLAG_REPEATED),
        }
