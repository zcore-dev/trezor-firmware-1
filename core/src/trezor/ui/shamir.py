from trezor import ui
from trezor.ui.button import Button, ButtonDefault


class NumInput(ui.Control):
    def __init__(self, count=5, max_count=16, min_count=1):
        self.max_count = max_count
        self.min_count = min_count

        class ButtonLabel(ButtonDefault):
            class disabled(ButtonDefault.normal):
                bg_color = ui.BG

        self.minus = Button(ui.grid(3), "-")
        self.minus.on_click = self.on_minus
        self.plus = Button(ui.grid(5), "+")
        self.plus.on_click = self.on_plus
        self.text = Button(ui.grid(4), "", ButtonLabel)
        self.text.disable()

        self.edit(count)

    def dispatch(self, event, x, y):
        self.minus.dispatch(event, x, y)
        self.plus.dispatch(event, x, y)
        self.text.dispatch(event, x, y)

    def on_minus(self):
        self.edit(self.count - 1)

    def on_plus(self):
        self.edit(self.count + 1)

    def edit(self, count):
        count = max(count, self.min_count)
        count = min(count, self.max_count)
        self.count = count
        self.text.content = str(count)
        self.text.repaint = True
        if self.count == self.min_count:
            self.minus.disable()
        else:
            self.minus.enable()
        if self.count == self.max_count:
            self.plus.disable()
        else:
            self.plus.enable()
