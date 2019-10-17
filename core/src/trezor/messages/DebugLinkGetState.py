# Automatically generated by pb2py
# fmt: off
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class DebugLinkGetState(p.MessageType):
    MESSAGE_WIRE_TYPE = 101

    def __init__(
        self,
        wait_word_list: bool = None,
        wait_word_pos: bool = None,
    ) -> None:
        self.wait_word_list = wait_word_list
        self.wait_word_pos = wait_word_pos

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('wait_word_list', p.BoolType, 0),
            2: ('wait_word_pos', p.BoolType, 0),
        }
