import pytest
from ui import Menu


@pytest.mark.parametrize(
    "title, expected_title",
    [
        ("MENU", "----- MENU -----"),
        ("12345", "---- 12345 -----"),
        ("CONFIG", "---- CONFIG ----"),
        ("1234567890", "-- 1234567890 --"),
        ("12345678901", "- 12345678901 --"),
        ("123456789012", "- 123456789012 -"),
        ("12345678901234", "-12345678901234-"),
        ("123456789012345", "123456789012345-"),
        ("1234567890123456", "1234567890123456"),
        ("1234567890123456789", "1234567890123456"),
    ],
)
def test_menu_title(title, expected_title):
    built_title = Menu.build_title(title)
    assert len(built_title) == 16
    assert built_title == expected_title
