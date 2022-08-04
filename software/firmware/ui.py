"""This module provides reusable UI components.
"""
from europi import CHAR_HEIGHT, CHAR_WIDTH, MAX_CHARACTERS, b1, k1, oled


class Menu:
    """A class representing a menu displayable on the EuroPi screen. The user can select a menu item using the
    configured knob and select it with the configured button(s).

    :param items: a list of the menu items
    :param select_func: the function to call when a menu item is chosen. The function will be called with single argument, the selected item.
    :param select_knob: the knob used to select the menu item, defaults to k1
    :param choice_buttons: a List of Buttons that can be pressed to choose the selected item. Defaults to b1
    :param title: a string that is shown at the top of the menu.
    """

    def __init__(self, items, select_func, select_knob=k1, choice_buttons=None, title="MENU"):
        self.items = items
        self.items.append(self.build_title(title))
        self.select_func = select_func
        self.select_knob = select_knob
        self.choice_buttons = choice_buttons or [b1]

        self.init_handlers()

    def init_handlers(self):
        def select():
            if self.selected != len(self.items) - 1:  # ignore the '-- MENU --' item
                self.select_func(self.items[self.selected])

        for b in self.choice_buttons:
            b.handler_falling(select)

    @staticmethod
    def build_title(title):
        l = len(title)
        use_spaces = l + 4 <= MAX_CHARACTERS
        title = f" {title} " if use_spaces else title
        return f"{title:-^{MAX_CHARACTERS}}"[0:MAX_CHARACTERS]

    @property
    def selected(self):
        """The currently selected menu item."""
        return self.select_knob.read_position(steps=len(self.items) - 1)

    def draw_menu(self):
        """This function should be called by your script's main loop in order to display and refresh the menu."""
        current = self.selected
        oled.fill(0)
        oled.text(f"{self.items[current - 1]}", 2, 3, 1)
        oled.inverted_text(f"{self.items[current]}", 2, 13)
        if current != len(self.items) - 2:
            # don't show the title at the bottom of the menu
            oled.text(f"{self.items[current + 1]}", 2, 23, 1)
        oled.show()
