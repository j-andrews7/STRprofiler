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


def test_mixing_requires_more_than_two_alleles():
    """The threshold counts markers with >2 alleles, so diploid calls never trip it."""
    diploid = {f"mark{i}": "1,2" for i in range(10)}

    assert sp.mixing_check(diploid, three_allele_threshold=0) is False


def test_mixing_ignores_metadata_columns():
    """Metadata values may contain commas but are not markers."""
    metadata_only = {
        "Center": "JAX,Bar Harbor,Farmington",
        "Passage": "P0,P1,P2",
        "mark1": "11,12",
    }

    assert sp.mixing_check(metadata_only, three_allele_threshold=0) is False


def test_mixing_metadata_cols_override():
    samp_meta = {"Site": "A,B,C", "mark1": "5,7,9"}

    assert sp.mixing_check(samp_meta, three_allele_threshold=0, metadata_cols=["Site"]) is True
    assert sp.mixing_check(samp_meta, three_allele_threshold=1, metadata_cols=["Site"]) is False


def test_mixing_ignores_non_numeric_alleles():
    """Off-ladder calls must not push a diploid marker over the tri-allelic threshold."""
    off_ladder = {f"mark{i}": "11,12,OL" for i in range(10)}

    assert sp.mixing_check(off_ladder, three_allele_threshold=0) is False


def test_mixing_counts_real_tri_allelic_markers():
    tri_allelic = {f"mark{i}": "11,12,13,OL" for i in range(4)}

    assert sp.mixing_check(tri_allelic, three_allele_threshold=3) is True
    assert sp.mixing_check(tri_allelic, three_allele_threshold=4) is False
