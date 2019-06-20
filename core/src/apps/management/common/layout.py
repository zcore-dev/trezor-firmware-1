from micropython import const

from trezor import ui
from trezor.crypto import random
from trezor.messages import ButtonRequestType, MessageType
from trezor.messages.ButtonRequest import ButtonRequest
from trezor.ui.mnemonic import MnemonicKeyboard
from trezor.ui.scroll import Paginated
from trezor.ui.text import Text
from trezor.utils import chunks, format_ordinal

from apps.common.confirm import hold_to_confirm, require_confirm

if __debug__:
    from apps import debug


async def show_mnemonics(ctx, mnemonics: list):
    # require confirmation of the mnemonic safety
    await show_warning(ctx)

    for i, mnemonic in enumerate(mnemonics, 1):
        if len(mnemonics) == 1:
            i = None
        # show mnemonic and require confirmation of a random word
        while True:
            words = mnemonic.split()
            await show_mnemonic(ctx, words, i)
            # if await check_mnemonic(ctx, words):
            break
            # await show_wrong_entry(ctx)


async def show_warning(ctx):
    text = Text("Backup your seed", ui.ICON_NOCOPY)
    text.normal(
        "Never make a digital",
        "copy of your recovery",
        "seed and never upload",
        "it online!",
    )
    await require_confirm(
        ctx, text, ButtonRequestType.ResetDevice, confirm="I understand", cancel=None
    )


async def show_wrong_entry(ctx):
    text = Text("Wrong entry!", ui.ICON_WRONG, icon_color=ui.RED)
    text.normal("You have entered", "wrong seed word.", "Please check again.")
    await require_confirm(
        ctx, text, ButtonRequestType.ResetDevice, confirm="Check again", cancel=None
    )


async def show_mnemonic(ctx, words: list, position: int):
    # split mnemonic words into pages
    PER_PAGE = const(4)
    words = list(enumerate(words))
    words = list(chunks(words, PER_PAGE))

    # display the pages, with a confirmation dialog on the last one
    pages = [get_mnemonic_page(page, position) for page in words]
    paginated = Paginated(pages)

    if __debug__:

        def export_displayed_words():
            # export currently displayed mnemonic words into debuglink
            debug.reset_current_words = [w for _, w in words[paginated.page]]

        paginated.on_change = export_displayed_words
        export_displayed_words()

    await hold_to_confirm(ctx, paginated, ButtonRequestType.ResetDevice)


def get_mnemonic_page(words: list, position: int):
    if position:
        text = Text("Recovery seed %d" % position, ui.ICON_RESET)
    else:
        text = Text("Recovery seed", ui.ICON_RESET)
    for index, word in words:
        text.mono("%2d. %s" % (index + 1, word))
    return text


async def check_mnemonic(ctx, words: list) -> bool:
    # check a word from the first half
    index = random.uniform(len(words) // 2)
    if not await check_word(ctx, words, index):
        return False

    # check a word from the second half
    index = random.uniform(len(words) // 2) + len(words) // 2
    if not await check_word(ctx, words, index):
        return False

    return True


async def check_word(ctx, words: list, index: int):
    if __debug__:
        debug.reset_word_index = index
    keyboard = MnemonicKeyboard("Type the %s word:" % format_ordinal(index + 1))
    if __debug__:
        result = await ctx.wait(keyboard, debug.input_signal)
    else:
        result = await ctx.wait(keyboard)
    return result == words[index]
