"""See config.md for details."""

from config_menu import ConfigMenu

from europi_config import EuroPiConfig
from contrib.diagnostic import Diagnostic
from contrib.turing_machine import EuroPiTuringMachine

# Scripts that are included in the config menu
CONFIG_CLASSES = [
    Diagnostic,
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
