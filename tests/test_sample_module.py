import pytest


@pytest.mark.parametrize(
    "a,b,expected",
    [
        pytest.param(1, 2, 3),
        pytest.param(-1, 1.0, 0),
    ],
)
def test_sample_func(a, b, expected):
    """Sample test case with parametrization."""
    # fake test
    assert True
