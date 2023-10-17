import strprofiler as sp
import pytest

inp = "10.0,10,13,13.0,14,14 "


@pytest.mark.parametrize("x", [(inp)])
def test_cleaning(x):
    assert sp._clean_element(x) == "10,13,14"
