import pytest
from pong import scale

@pytest.mark.parametrize("value, istart, istop, ostart, ostop, expected", [
    (5, 0, 10, 0, 10, 5),
    (5, 0, 10, 0, 100, 50),
    (5, 0, 10, 0, 1000, 500),
    (5, 0, 10, 0, 1000, 500),
])
def test_scale(value, istart, istop, ostart, ostop, expected):
    assert scale(value, istart, istop, ostart, ostop) == expected