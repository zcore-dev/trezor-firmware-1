from common import *
from ubinascii import unhexlify

from trezor.messages.BinanceOrderMsg import BinanceOrderMsg
from trezor.messages.BinanceSignTx import BinanceSignTx

from apps.binance.helpers import produce_json_for_signing, encode_binary_address, binary_to_bech
from apps.binance.sign_tx import generate_content_signature, verify_content_signature
from apps.binance.serialize import encode_std_signature, encode_order_msg, encode

class TestBinanceSerialze(unittest.TestCase):
    def testEncodeAddressToBinary(self):
        bech32_address = "tbnb1hgm0p7khfk85zpz5v0j8wnej3a90w709zzlffd"
        encoded_address = unhexlify("BA36F0FAD74D8F41045463E4774F328F4AF779E5")

        self.assertEqual(encode_binary_address(bech32_address), encoded_address)

    def testEncodeToBinary(self):
        #source of testing data https://github.com/binance-chain/javascript-sdk/blob/master/__tests__/encoder.test.js#L64
        pubkey_hex = "03baf53d1424f8ea83d03a82f6d157b5401c4ea57ffb8317872e15a19fc9b7ad7b"
        signature_hex = "e79a6606d28cf07b9cc6f566b524a5282b13beccc3162376c79f392620c95a447b19f64e761e22a7a3bc311a780e7d9fdd521e2f7edec25308c5bac6aa1c0a31"
        expected_encoded_msg = "db01f0625dee0a65ce6dc0430a14b6561dcc104130059a7c08f48c64610c1f6f9064122b423635363144434331303431333030353941374330384634384336343631304331463646393036342d31311a0b4254432d3543345f424e42200228013080c2d72f3880989abc044001126e0a26eb5ae9872103baf53d1424f8ea83d03a82f6d157b5401c4ea57ffb8317872e15a19fc9b7ad7b1240e79a6606d28cf07b9cc6f566b524a5282b13beccc3162376c79f392620c95a447b19f64e761e22a7a3bc311a780e7d9fdd521e2f7edec25308c5bac6aa1c0a311801200a"

        envelope = BinanceSignTx(account_number=1, chain_id="bnbchain-1000", memo="", sequence=10)
        msg = BinanceOrderMsg(id="B6561DCC104130059A7C08F48C64610C1F6F9064-11",
                              ordertype=2,
                              price=100000000,
                              quantity=1200000000,
                              sender="tbnb1ketpmnqsgycqtxnupr6gcerpps0klyryjfyx09",
                              side=1,
                              symbol="BTC-5C4_BNB",
                              timeinforce=1)

        encoded = encode(envelope, msg, unhexlify(signature_hex), unhexlify(pubkey_hex))
        self.assertEqual(hexlify(encoded), expected_encoded_msg.encode())
    

if __name__ == '__main__':
    unittest.main()
