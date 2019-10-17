# Automatically generated by pb2py
# fmt: off
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class EosAuthorizationWait(p.MessageType):

    def __init__(
        self,
        wait_sec: int = None,
        weight: int = None,
    ) -> None:
        self.wait_sec = wait_sec
        self.weight = weight

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('wait_sec', p.UVarintType, 0),
            2: ('weight', p.UVarintType, 0),
        }
