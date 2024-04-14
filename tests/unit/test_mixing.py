import strprofiler.utils as sp
import pytest

samp = {
    "mark1": "11,12",
    "mark2": "3",
    "mark3": "13,14",
    "mark4": "5,7,9",
    "mark5": "5,7,9",
    "mark6": "5,7,9",
    "mark7": "5,7,9",
    "AMEL": "X",
}


@pytest.mark.parametrize("alleles, three_allele_threshold, expected", [(samp, 3, True), (samp, 5, False)])
def test_mixing(alleles, three_allele_threshold, expected):
    assert sp.mixing_check(alleles, three_allele_threshold=three_allele_threshold) == expected
