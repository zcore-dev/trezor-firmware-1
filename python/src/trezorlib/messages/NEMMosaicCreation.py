# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

from .NEMMosaicDefinition import NEMMosaicDefinition

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class NEMMosaicCreation(p.MessageType):

    def __init__(
        self,
        definition: NEMMosaicDefinition = None,
        sink: str = None,
        fee: int = None,
    ) -> None:
        self.definition = definition
        self.sink = sink
        self.fee = fee

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('definition', NEMMosaicDefinition, 0),
            2: ('sink', p.UnicodeType, 0),
            3: ('fee', p.UVarintType, 0),
        }
