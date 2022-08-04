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
        print(f"selected {selected_item}")

    def back(self):
        self.exit_requested = True
        print("back")

    def main(self):
        # let the user make a selection
        print("enter config menu")
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
        print("enter script menu")
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
                self.display_config_point(config_points.points[self.config_point_choice], config)
            self.config_point_choice = None
        self.exit_requested = False

    def display_config_point(self, config_point, config):
        if config_point["type"] == "choice":
            self.display_config_point_choice(config_point, config)

    def display_config_point_choice(self, config_point, config):
        print("enter choice")
        while not self.exit_requested:
            europi.oled.fill(0)
            europi.oled.text(f"{config_point['name']}:", 2, 3, 1)
            europi.oled.inverted_text(
                f"{config[config_point['name']]: >{europi.MAX_CHARACTERS}}", 0, 13
            )
            europi.oled.text(
                f"{europi.k2.choice(config_point['choices']): >{europi.MAX_CHARACTERS}}", 0, 23, 1
            )
            europi.oled.show()
            time.sleep(0.1)

        self.exit_requested = False


if __name__ == "__main__":
    ConfigMenu(CONFIG_CLASSES).main()
