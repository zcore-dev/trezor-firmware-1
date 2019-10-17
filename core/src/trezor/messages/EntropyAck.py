# Automatically generated by pb2py
# fmt: off
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class EntropyAck(p.MessageType):
    MESSAGE_WIRE_TYPE = 36

    def __init__(
        self,
        entropy: bytes = None,
    ) -> None:
        self.entropy = entropy

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('entropy', p.BytesType, 0),
        }
