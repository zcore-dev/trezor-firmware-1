# Automatically generated by pb2py
import protobuf as p
from micropython import const
t = p.MessageType('DecryptedMessage')
t.wire_type = 52
t.add_field(1, 'message', p.BytesType)
t.add_field(2, 'address', p.UnicodeType)
DecryptedMessage = t