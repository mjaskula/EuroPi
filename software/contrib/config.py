"""See config.md for details."""

from config_menu import ConfigMenu

from contrib.turing_machine import EuroPiTuringMachine
from contrib.europi_config import EuroPiConfig

# Scripts that are included in the config menu
CONFIG_CLASSES = [
    EuroPiTuringMachine,
    EuroPiConfig,
]


class Config(ConfigMenu):
    def __init__(self) -> None:
        super().__init__(CONFIG_CLASSES)

    @classmethod
    def display_name(cls):
        """Push this script to the end of the menu."""
        return "~Config"
