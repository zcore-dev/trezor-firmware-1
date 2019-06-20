from trezor.crypto import bip39

from apps.common import mnemonic, storage


def generate(secret: bytes, count: int = None, threshold: int = None) -> list:
    """
    Generates new mnemonics as defined in BIP-39. Returns list of
    words wrapped in a list.
    """
    if count or threshold:
        raise NotImplementedError("Shares count or threshold not applicable to BIP-39")
    return [bip39.from_data(secret)]


def get_seed(secret: bytes, passphrase: str = ""):
    mnemonic._start_progress()
    return bip39.seed(secret.decode(), passphrase, mnemonic._render_progress)


def get_type():
    return mnemonic.TYPE_BIP39


def process_single(words: str) -> bytes:
    """
    Receives single mnemonic and processes it.
    Returns None if more shares are needed.
    """
    return " ".join(words).encode()


def store(secret: bytes, needs_backup: bool = False, no_backup: bool = False):
    storage.store_mnemonic(secret, mnemonic.TYPE_BIP39, needs_backup, no_backup)


def restore() -> str:
    secret, mnemonic_type = mnemonic.get()
    return secret.decode()


def check(secret: bytes):
    return bip39.check(secret)
