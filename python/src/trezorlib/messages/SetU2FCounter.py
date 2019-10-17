# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class SetU2FCounter(p.MessageType):
    MESSAGE_WIRE_TYPE = 63

    def __init__(
        self,
        u2f_counter: int = None,
    ) -> None:
        self.u2f_counter = u2f_counter

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('u2f_counter', p.UVarintType, 0),
        }
