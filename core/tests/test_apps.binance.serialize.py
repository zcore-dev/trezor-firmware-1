from common import *
from ubinascii import unhexlify

from trezor.messages.BinanceCancelMsg import BinanceCancelMsg
from trezor.messages.BinanceCoin import BinanceCoin
from trezor.messages.BinanceInputOutput import BinanceInputOutput
from trezor.messages.BinanceOrderMsg import BinanceOrderMsg
from trezor.messages.BinanceSignTx import BinanceSignTx
from trezor.messages.BinanceTransferMsg import BinanceTransferMsg

from apps.binance.helpers import produce_json_for_signing, encode_binary_address, encode_binary_amount
from apps.binance.sign_tx import generate_content_signature, verify_content_signature
from apps.binance.serialize import encode_std_signature, encode_order_msg, encode

class TestBinanceSerialze(unittest.TestCase):
    def test_encode_address_to_binary(self):
        bech32_address = "tbnb1hgm0p7khfk85zpz5v0j8wnej3a90w709zzlffd"
        expected_encoded_address = unhexlify("BA36F0FAD74D8F41045463E4774F328F4AF779E5")

        self.assertEqual(encode_binary_address(bech32_address), expected_encoded_address)


    def test_encode_amount_to_binary(self):
        amount = 100000000
        expected_encoded_amount = unhexlify("80c2d72f")

        self.assertEqual(encode_binary_amount(amount), expected_encoded_amount)


    def test_encode_order_to_binary(self):
        #source of testing data https://github.com/binance-chain/javascript-sdk/blob/master/__tests__/fixtures/placeOrder.json
        pubkey_hex = "029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e"
        signature_hex = "851fc9542342321af63ecbba7d3ece545f2a42bad01ba32cff5535b18e54b6d3106e10b6a4525993d185a1443d9a125186960e028eabfdd8d76cf70a3a7e3100"
        expected_encoded_msg = "de01f0625dee0a66ce6dc0430a14ba36f0fad74d8f41045463e4774f328f4af779e5122b424133364630464144373444384634313034353436334534373734463332384634414637373945352d33331a0d4144412e422d4236335f424e42200428023080c2d72f3880c2d72f4002126e0a26eb5ae98721029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e1240851fc9542342321af63ecbba7d3ece545f2a42bad01ba32cff5535b18e54b6d3106e10b6a4525993d185a1443d9a125186960e028eabfdd8d76cf70a3a7e3100182220202001"

        envelope = BinanceSignTx(account_number=34, chain_id="Binance-Chain-Nile", memo="", sequence=32, source=1)
        msg = BinanceOrderMsg(id="BA36F0FAD74D8F41045463E4774F328F4AF779E5-33",
                              ordertype=4,
                              price=100000000,
                              quantity=100000000,
                              sender="tbnb1hgm0p7khfk85zpz5v0j8wnej3a90w709zzlffd",
                              side=2,
                              symbol="ADA.B-B63_BNB",
                              timeinforce=2)
        msgs = [msg]

        encoded = encode(envelope, msgs, unhexlify(signature_hex), unhexlify(pubkey_hex))
        self.assertEqual(hexlify(encoded), expected_encoded_msg.encode())


    def test_encode_cancel_to_binary(self):
        #source of testing data https://github.com/binance-chain/javascript-sdk/blob/master/__tests__/fixtures/cancelOrder.json
        pubkey_hex = "029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e"
        signature_hex = "d93fb0402b2b30e7ea08e123bb139ad68bf0a1577f38592eb22d11e127f09bbd3380f29b4bf15bdfa973454c5c8ed444f2e256e956fe98cfd21e886a946e21e5"
        expected_encoded_msg = "d001f0625dee0a58166e681b0a14ba36f0fad74d8f41045463e4774f328f4af779e5120f42434853562e422d3130465f424e421a2b424133364630464144373444384634313034353436334534373734463332384634414637373945352d3239126e0a26eb5ae98721029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e1240d93fb0402b2b30e7ea08e123bb139ad68bf0a1577f38592eb22d11e127f09bbd3380f29b4bf15bdfa973454c5c8ed444f2e256e956fe98cfd21e886a946e21e5182220212001"

        envelope = BinanceSignTx(account_number=34, chain_id="Binance-Chain-Nile", memo="", sequence=33, source=1)
        msg = BinanceCancelMsg(refid="BA36F0FAD74D8F41045463E4774F328F4AF779E5-29", 
                               sender="tbnb1hgm0p7khfk85zpz5v0j8wnej3a90w709zzlffd", 
                               symbol="BCHSV.B-10F_BNB")
        msgs = [msg]

        encoded = encode(envelope, msgs, unhexlify(signature_hex), unhexlify(pubkey_hex))
        self.assertEqual(hexlify(encoded), expected_encoded_msg.encode())


    def test_encode_transfer_to_binary(self):
        #https://github.com/binance-chain/javascript-sdk/blob/master/__tests__/fixtures/transfer.json
        pubkey_hex = "029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e"
        signature_hex = "97b4c2e41b0d0f61ddcf4020fff0ecb227d6df69b3dd7e657b34be0e32b956e22d0c6be5832d25353ae24af0bb223d4a5337320518c4e7708b84c8e05eb6356b"
        expected_encoded_msg = "cc01f0625dee0a4e2a2c87fa0a230a14ba36f0fad74d8f41045463e4774f328f4af779e5120b0a03424e42108094ebdc0312230a148429ec9e1df1a6e03e2fb2b0b1fbd4e770544848120b0a03424e42108094ebdc03126e0a26eb5ae98721029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e124097b4c2e41b0d0f61ddcf4020fff0ecb227d6df69b3dd7e657b34be0e32b956e22d0c6be5832d25353ae24af0bb223d4a5337320518c4e7708b84c8e05eb6356b1822201f1a04746573742001"

        envelope = BinanceSignTx(account_number=34, chain_id="Binance-Chain-Nile", memo="test", sequence=31, source=1)
        coin = BinanceCoin(denom="BNB", amount=1000000000)
        first_input = BinanceInputOutput(address="tbnb1hgm0p7khfk85zpz5v0j8wnej3a90w709zzlffd", coins=[coin])
        first_output = BinanceInputOutput(address="tbnb1ss57e8sa7xnwq030k2ctr775uac9gjzglqhvpy", coins=[coin])
        msg = BinanceTransferMsg(inputs=[first_input], outputs=[first_output])
        msgs = [msg]

        encoded = encode(envelope, msgs, unhexlify(signature_hex), unhexlify(pubkey_hex))
        self.assertEqual(hexlify(encoded), expected_encoded_msg.encode())


if __name__ == '__main__':
    unittest.main()
