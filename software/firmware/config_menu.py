"""See config.md for details."""
from collections import OrderedDict
import time

import europi
from europi_script import EuroPiScript
from ui import Menu


class ConfigMenu(EuroPiScript):
    """"""

    def __init__(self, config_classes):
        self.scripts_config = ConfigMenu._build_scripts_config(config_classes)
        self.menu = Menu(
            items=list(sorted(self.scripts_config.keys())),
            select_func=self.select_script,
            select_knob=europi.k2,
            choice_buttons=[europi.b2],
            title="CONFIG",
        )
        self.script_choice = None
        self.config_point_choice = None
        self.exit_requested = False
        self.write_requested = False

        europi.b1.handler_falling(self.back)

    @staticmethod
    def _build_scripts_config(classes):
        return OrderedDict(
            [(cls.display_name(), cls) for cls in classes if issubclass(cls, EuroPiScript)]
        )

    def select_script(self, selected_item):
        self.script_choice = selected_item

    def select_config_point(self, selected_item):
        self.config_point_choice = selected_item

    def back(self):
        self.exit_requested = True

    def main(self):
        # let the user make a selection
        while True:
            old_selected = -1
            while not self.script_choice:
                if old_selected != self.menu.selected:
                    old_selected = self.menu.selected
                    self.menu.draw_menu()

            self.script_config_menu(self.script_choice)
            # reinstate the menu's handlers
            self.menu.init_handlers()
            self.script_choice = None

    def script_config_menu(self, script_choice):
        cls = self.scripts_config[script_choice]
        config_points = cls._build_config_points()
        config = cls._load_config()

        sub_menu = Menu(
            items=list(sorted(config_points.points.keys())),
            select_func=self.select_config_point,
            select_knob=europi.k2,
            choice_buttons=[europi.b2],
            title=script_choice,
        )

        while not self.exit_requested:
            old_selected = None
            while not self.config_point_choice and not self.exit_requested:
                if old_selected != sub_menu.selected:
                    old_selected = sub_menu.selected
                    sub_menu.draw_menu()
            if self.config_point_choice:
                self.edit_config_point(cls, config_points.points[self.config_point_choice], config)
                sub_menu.init_handlers()
                self.config_point_choice = None
        self.exit_requested = False

    def edit_config_point(self, cls, config_point, config):
        def request_write():
            self.write_requested = True

        europi.b2.handler_falling(request_write)

        if config_point["type"] == "choice":
            self.edit_config_point_choice(cls, config_point, config)

    def inverted_text(self, s, x, y):
        """displays the given text with an inverted background"""
        europi.oled.fill_rect(x, y - 1, europi.CHAR_WIDTH * len(s), europi.CHAR_HEIGHT + 2, 1)
        europi.oled.text(s, x, y, 0)

    def edit_config_point_choice(self, cls, config_point, config):

        while not self.exit_requested:
            europi.oled.fill(0)
            europi.oled.text(f"{config_point['name']}:", 2, 3, 1)
            if self.write_requested:
                self.inverted_text(f"{'writing...': ^{europi.MAX_CHARACTERS}}", 0, 13)
            else:
                self.inverted_text(
                    f"{config[config_point['name']]: >{europi.MAX_CHARACTERS}}", 0, 13
                )
            europi.oled.text(
                f"{europi.k2.choice(config_point['choices']): >{europi.MAX_CHARACTERS}}", 0, 23, 1
            )
            europi.oled.show()
            if self.write_requested:
                config[config_point["name"]] = europi.k2.choice(config_point["choices"])
                cls._save_config(config)
                self.write_requested = False
