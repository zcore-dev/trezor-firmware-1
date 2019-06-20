from trezor.crypto import slip39

from apps.common import mnemonic, storage

_DEFAULT_ITERATION_EXPONENT = 0


def generate(master_secret: bytes, count: int = None, threshold: int = None) -> list:
    """
    Generates new Shamir backup for 'master_secret'.
    Multiple groups are not yet supported.
    """
    identifier, group_mnemonics = slip39.generate_mnemonics(
        1,
        [(threshold, count)],
        master_secret,
        passphrase="",
        iteration_exponent=_DEFAULT_ITERATION_EXPONENT,
    )
    storage.set_slip39_iteration_exponent(_DEFAULT_ITERATION_EXPONENT)
    storage.set_slip39_identifier(identifier)
    return group_mnemonics[0]


def get_type():
    return mnemonic.TYPE_SLIP39


def process_single(mnemonic: str) -> bytes:
    """
    Receives single mnemonic and processes it.
    Returns None if more shares are needed.
    """
    # TODO: this is quite ugly
    identifier, iteration_exponent, _, _, _, index, threshold, value = slip39.decode_mnemonic(
        mnemonic
    )
    if threshold == 1:
        raise ValueError("Threshold equal to 1 is not allowed.")

    if not storage.is_slip39_in_progress():
        storage.set_slip39_in_progress(True)
        storage.set_slip39_iteration_exponent(iteration_exponent)
        storage.set_slip39_identifier(identifier)
        storage.set_slip39_threshold(threshold)
        storage.set_slip39_remaining(threshold - 1)
        storage.set_slip39_words_count(len(mnemonic.split()))
        storage.set_slip39_mnemonic(index, mnemonic)
        return None
    else:
        if identifier != storage.get_slip39_identifier():
            # TODO improve UX (tell user)
            raise ValueError(
                "Share identifiers do not match %s vs %s",
                identifier,
                storage.get_slip39_identifier(),
            )
        if storage.get_slip39_mnemonic(index):
            # TODO improve UX (tell user)
            raise ValueError("This mnemonic was already entered")
        remaining = storage.get_slip39_remaining() - 1
        storage.set_slip39_remaining(remaining)
        storage.set_slip39_mnemonic(index, mnemonic)
        if remaining != 0:
            return None

    # combine shares and returns
    mnemonics = storage.get_slip39_mnemonics()
    if len(mnemonics) != threshold:
        raise ValueError("Some mnemonics are still missing.")
    _, _, secret = slip39.combine_mnemonics(mnemonics)
    return secret


def store(secret: bytes, needs_backup: bool = False, no_backup: bool = False):
    storage.store_mnemonic(secret, mnemonic.TYPE_SLIP39, needs_backup, no_backup)
    storage.clear_slip39_data()


def restore() -> str:
    raise NotImplementedError()


def get_seed(encrypted_master_secret: bytes, passphrase: str = ""):
    mnemonic._start_progress()
    identifier = storage.get_slip39_identifier()
    iteration_exponent = storage.get_slip39_iteration_exponent()
    return slip39.decrypt(
        identifier, iteration_exponent, encrypted_master_secret, passphrase
    )
