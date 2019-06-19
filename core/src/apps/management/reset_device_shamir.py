from trezor import ui, utils
from trezor.crypto import random
from trezor.messages import ButtonRequestType
from trezor.ui.button import Button, ButtonDefault
from trezor.ui.checklist import Checklist
from trezor.ui.info import InfoConfirm
from trezor.ui.loader import LoadingAnimation
from trezor.ui.scroll import Paginated
from trezor.ui.shamir import NumInput
from trezor.ui.text import Text

from apps.common.confirm import confirm, hold_to_confirm, require_confirm

# TODO: yellow cancel style?
# TODO: loading animation style?
# TODO: smaller font or tighter rows to fit more text in
# TODO: icons in checklist


async def reset_device_shamir(ctx, msg):

    # confirm start of the reset device workflow
    await require_confirm_reset_device(ctx)

    # TODO: compute mnemonic

    if not msg.skip_backup and not msg.no_backup:

        # confirm that the mnemonic has been generated
        if not await confirm_backup(ctx):
            if not await confirm_backup_again(ctx):
                pass

        # get number of shares
        await show_checklist_set_shares(ctx)
        num_of_shares = await prompt_number_of_shares(ctx)

        # get treshold
        await show_checklist_set_treshold(ctx, num_of_shares)
        treshold = await prompt_threshold(ctx, num_of_shares)

        # TODO: compute the shares
        shares = [["all"] * 20] * num_of_shares

        # show and confirm individual shares
        await show_checklist_show_shares(ctx, num_of_shares, treshold)
        await show_and_confirm_shares(ctx, shares)


async def require_confirm_reset_device(ctx):
    text = Text("Create new wallet", ui.ICON_RESET, new_lines=False)
    text.bold("Do you want to create")
    text.br()
    text.bold("a new wallet?")
    text.br()
    text.br_half()
    text.normal("By continuing you agree")
    text.br()
    text.normal("to")
    text.bold("https://trezor.io/tos")
    await require_confirm(
        ctx, text, code=ButtonRequestType.ResetDevice, major_confirm=True
    )
    await LoadingAnimation()


async def confirm_backup(ctx):
    text = Text("Backup wallet", ui.ICON_RESET, new_lines=False)
    text.bold("New wallet created")
    text.br()
    text.bold("successfully!")
    text.br()
    text.br_half()
    text.normal("You should back your")
    text.br()
    text.normal("new wallet right now.")
    return await confirm(
        ctx,
        text,
        code=ButtonRequestType.ResetDevice,
        cancel="Skip",
        confirm="Backup",
        major_confirm=True,
    )


async def confirm_backup_again(ctx):
    text = Text("Backup wallet", ui.ICON_RESET, new_lines=False)
    text.bold("Are you sure you want")
    text.br()
    text.bold("to skip the backup?")
    text.br()
    text.br_half()
    text.normal("You can backup Trezor")
    text.br()
    text.normal("anytime later.")
    return await confirm(
        ctx,
        text,
        code=ButtonRequestType.ResetDevice,
        cancel="Skip",
        confirm="Backup",
        major_confirm=True,
    )


async def show_checklist_set_shares(ctx):
    checklist = Checklist("Backup checklist", ui.ICON_RESET)
    checklist.add("Set number of shares")
    checklist.add("Set the treshold")
    checklist.add(("Write down and check", "all seed shares"))
    checklist.select(0)
    checklist.process()
    return await confirm(
        ctx,
        checklist,
        code=ButtonRequestType.ResetDevice,
        cancel=None,
        confirm="Set shares",
    )


async def show_checklist_set_treshold(ctx, num_of_shares):
    checklist = Checklist("Backup checklist", ui.ICON_RESET)
    checklist.add("Set number of shares")
    checklist.add("Set the treshold")
    checklist.add(("Write down and check", "all seed shares"))
    checklist.select(1)
    checklist.process()
    return await confirm(
        ctx,
        checklist,
        code=ButtonRequestType.ResetDevice,
        cancel=None,
        confirm="Set treshold",
    )


async def show_checklist_show_shares(ctx, num_of_shares, treshold):
    checklist = Checklist("Backup checklist", ui.ICON_RESET)
    checklist.add("Set number of shares")
    checklist.add("Set the treshold")
    checklist.add(("Write down and check", "all seed shares"))
    checklist.select(2)
    checklist.process()
    return await confirm(
        ctx,
        checklist,
        code=ButtonRequestType.ResetDevice,
        cancel=None,
        confirm="Show seed shares",
    )


async def prompt_number_of_shares(ctx):
    count = 5
    max_count = 16

    while True:
        shares = ShamirNumInput(ShamirNumInput.SET_SHARES, count, max_count)
        info = InfoConfirm(
            "Shares are parts of "
            "the recovery seed, "
            "each containing 20 "
            "words. You can later set "
            "how many shares you "
            "need to recover your "
            "wallet."
        )
        confirmed = await confirm(
            ctx,
            shares,
            code=ButtonRequestType.ResetDevice,
            cancel="Info",
            confirm="Set",
            major_confirm=True,
            cancel_style=ButtonDefault,
        )
        count = shares.input.count
        if confirmed:
            break
        else:
            await info

    return count


async def prompt_threshold(ctx, num_of_shares):
    count = num_of_shares // 2
    max_count = num_of_shares

    while True:
        shares = ShamirNumInput(ShamirNumInput.SET_TRESHOLD, count, max_count)
        info = InfoConfirm(
            "Treshold sets number "
            "shares that you need "
            "to recover your wallet. "
            "i.e. Set it to %s and "
            "you'll need any %s shares "
            "of the total number." % (count, count)
        )
        confirmed = await confirm(
            ctx,
            shares,
            code=ButtonRequestType.ResetDevice,
            cancel="Info",
            confirm="Set",
            major_confirm=True,
            cancel_style=ButtonDefault,
        )
        count = shares.input.count
        if confirmed:
            break
        else:
            await info

    return count


async def show_and_confirm_shares(ctx, shares):
    for index, share in enumerate(shares):
        while True:
            await show_share(ctx, index, share)
            if await confirm_share(ctx, index, share):
                await show_confirmation_success(ctx, index)
                break  # this share is confirmed, go to next one


async def show_share(ctx, share_index, share):
    first, chunks, last = split_share_into_pages(share)

    header_title = "Recovery share #%s" % (share_index + 1)
    header_icon = ui.ICON_RESET
    pages = []  # ui page components

    # first page
    text = Text(header_title, header_icon)
    text.normal("Write down %s words" % len(share))
    text.normal("onto paper booklet:")
    text.br_half()
    for index, word in first:
        text.mono("%s. %s" % (index + 1, word))
    pages.append(text)

    # middle pages
    for chunk in chunks:
        text = Text(header_title, header_icon)
        text.br_half()
        for index, word in chunk:
            text.mono("%s. %s" % (index + 1, word))
        pages.append(text)

    # last page
    text = Text(header_title, header_icon)
    for index, word in last:
        text.mono("%s. %s" % (index + 1, word))
    text.br_half()
    text.normal("I confirm that I wrote")
    text.normal("down all %s words." % len(share))
    pages.append(text)

    # pagination
    paginated = Paginated(pages)

    # confirm the share
    await hold_to_confirm(ctx, paginated)  # TODO: customize the loader here


async def confirm_share(ctx, share_index, share):
    numbered = list(enumerate(share))
    # check a word from the first half
    first_half = numbered[: len(numbered) // 2]
    if not await confirm_word(ctx, share_index, first_half):
        return False
    # check a word from the second half
    second_half = numbered[len(numbered) // 2 :]
    if not await confirm_word(ctx, share_index, second_half):
        return False
    return True


async def confirm_word(ctx, share_index, numbered_share):
    # TODO: duplicated words in the choice list
    # shuffle the numbered seed half, slice off the choices we need
    random.shuffle(numbered_share)
    numbered_choices = numbered_share[: ShamirWordSelect.NUM_OF_CHOICES]
    # we always confirm the first (random) word index
    checked_index, checked_word = numbered_choices[0]
    # shuffle again so the confirmed word is not always the first choice
    random.shuffle(numbered_choices)
    # take just the words
    choices = [word for _, word in numbered_choices]
    # let the user pick a word
    select = ShamirWordSelect(choices, share_index, checked_index)
    selected_word = await select
    # confirm it is the correct one
    return selected_word == checked_word


def split_share_into_pages(share):
    share = list(enumerate(share))  # we need to keep track of the word indices
    first = share[:2]  # two words on the first page
    middle = share[2:-2]
    last = share[-2:]  # two words on the last page
    chunks = utils.chunks(middle, 4)  # 4 words on the middle pages
    return first, list(chunks), last


async def show_confirmation_success(ctx, share_index):
    text = Text("Recovery share #%s" % (share_index + 1), ui.ICON_RESET)
    text.bold("Seed share #%s" % (share_index + 1))
    text.bold("checked successfully.")
    text.normal("Let's continue with")
    text.normal("share #%s." % (share_index + 2))
    return await confirm(
        ctx, text, code=ButtonRequestType.ResetDevice, cancel=None, confirm="Continue"
    )


class ShamirNumInput(ui.Control):
    SET_SHARES = object()
    SET_TRESHOLD = object()

    def __init__(self, step, count, max_count):
        self.step = step
        self.input = NumInput(count, max_count)
        self.input.on_change = self.on_change
        self.repaint = True

    def dispatch(self, event, x, y):
        self.input.dispatch(event, x, y)
        if event is ui.RENDER:
            self.on_render()

    def on_render(self):
        if self.repaint:
            count = self.input.count

            # render the headline
            if self.step is ShamirNumInput.SET_SHARES:
                header = "Set num. of shares"
            elif self.step is ShamirNumInput.SET_TRESHOLD:
                header = "Set the treshold"
            ui.header(header, ui.ICON_RESET, ui.TITLE_GREY, ui.BG, ui.ORANGE_ICON)

            # render the counter
            if self.step is ShamirNumInput.SET_SHARES:
                ui.display.text(
                    12, 130, "%s people or locations" % count, ui.BOLD, ui.FG, ui.BG
                )
                ui.display.text(
                    12, 156, "will each host one share.", ui.NORMAL, ui.FG, ui.BG
                )
            elif self.step is ShamirNumInput.SET_TRESHOLD:
                ui.display.text(
                    12, 130, "For recovery you'll need", ui.NORMAL, ui.FG, ui.BG
                )
                ui.display.text(
                    12, 156, "any %s of shares." % count, ui.BOLD, ui.FG, ui.BG
                )

            self.repaint = False

    def on_change(self, count):
        self.repaint = True


class ShamirWordSelect(ui.Layout):
    NUM_OF_CHOICES = 3

    def __init__(self, words, share_index, word_index):
        self.words = words
        self.share_index = share_index
        self.word_index = word_index
        self.buttons = []
        for i, word in enumerate(words):
            area = ui.grid(i + 2, n_x=1)
            btn = Button(area, word)
            btn.on_click = self.select(word)
            self.buttons.append(btn)
        self.text = Text("Recovery share #%s" % (share_index + 1))
        self.text.normal("Choose the %s word:" % utils.format_ordinal(word_index + 1))

    def dispatch(self, event, x, y):
        for btn in self.buttons:
            btn.dispatch(event, x, y)
        self.text.dispatch(event, x, y)

    def select(self, word):
        def fn():
            raise ui.Result(word)

        return fn
