# Automatically generated by pb2py
import protobuf as p
from micropython import const
t = p.MessageType('CoinType')
t.add_field(1, 'coin_name', p.UnicodeType)
t.add_field(2, 'coin_shortcut', p.UnicodeType)
t.add_field(3, 'address_type', p.UVarintType, default=0)
t.add_field(4, 'maxfee_kb', p.UVarintType)
t.add_field(5, 'address_type_p2sh', p.UVarintType, default=5)
t.add_field(6, 'address_type_p2wpkh', p.UVarintType, default=6)
t.add_field(7, 'address_type_p2wsh', p.UVarintType, default=10)
CoinType = t