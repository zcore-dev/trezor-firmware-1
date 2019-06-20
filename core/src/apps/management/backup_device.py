from trezor import wire
from trezor.messages.Success import Success

from apps.common import mnemonic, storage
from apps.management.common import layout
from apps.management.reset_device import (
    check_mnemonic,
    show_backup_warning,
    show_mnemonic,
    show_wrong_entry,
)


async def backup_device(ctx, msg):
    # TODO: support SLIP-39
    if not storage.is_initialized():
        raise wire.ProcessError("Device is not initialized")
    if not storage.needs_backup():
        raise wire.ProcessError("Seed already backed up")

    words = mnemonic.restore()

    # warn user about mnemonic safety
    await show_backup_warning(ctx)

    storage.set_unfinished_backup(True)
    storage.set_backed_up()

    words = mnemonic.bip39.restore()
    mnemonics = [words.split(" ")]
    await layout.show_mnemonics(ctx, mnemonics)

    storage.set_unfinished_backup(False)

    return Success(message="Seed successfully backed up")
