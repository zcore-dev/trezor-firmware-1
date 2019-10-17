# Automatically generated by pb2py
# fmt: off
import protobuf as p

from .LiskDelegateType import LiskDelegateType
from .LiskMultisignatureType import LiskMultisignatureType
from .LiskSignatureType import LiskSignatureType

if __debug__:
    try:
        from typing import Dict, List, Optional
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class LiskTransactionAsset(p.MessageType):

    def __init__(
        self,
        signature: LiskSignatureType = None,
        delegate: LiskDelegateType = None,
        votes: List[str] = None,
        multisignature: LiskMultisignatureType = None,
        data: str = None,
    ) -> None:
        self.signature = signature
        self.delegate = delegate
        self.votes = votes if votes is not None else []
        self.multisignature = multisignature
        self.data = data

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('signature', LiskSignatureType, 0),
            2: ('delegate', LiskDelegateType, 0),
            3: ('votes', p.UnicodeType, p.FLAG_REPEATED),
            4: ('multisignature', LiskMultisignatureType, 0),
            5: ('data', p.UnicodeType, 0),
        }
