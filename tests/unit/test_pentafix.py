import strprofiler.utils as sp
import pandas as pd
import pytest


@pytest.mark.parametrize(
    "src, dest",
    [
        ("Penta C", "PentaC"),
        ("Penta_C", "PentaC"),
        ("Penta D", "PentaD"),
        ("Penta_D", "PentaD"),
        ("Penta E", "PentaE"),
        ("Penta_E", "PentaE"),
    ],
)
def test_pentafix_forward(src, dest):
    assert sp._pentafix({src: "9,10", "vWA": "16"}) == {dest: "9,10", "vWA": "16"}


@pytest.mark.parametrize(
    "src, dest",
    [
        ("PentaC", "Penta C"),
        ("Penta_C", "Penta C"),
        ("PentaD", "Penta D"),
        ("Penta_D", "Penta D"),
        ("PentaE", "Penta E"),
        ("Penta_E", "Penta E"),
    ],
)
def test_pentafix_reverse(src, dest):
    assert sp._pentafix({src: "9,10", "vWA": "16"}, reverse=True) == {
        dest: "9,10",
        "vWA": "16",
    }


def test_pentafix_no_penta_markers():
    samp = {"vWA": "16,18", "TH01": "7,9.3"}
    assert sp._pentafix(dict(samp)) == samp
    assert sp._pentafix(dict(samp), reverse=True) == samp


def test_pentafix_merges_colliding_spellings():
    """Both spellings for one sample must be merged, not overwritten."""
    assert sp._pentafix({"PentaD": "9,10", "Penta D": "11,12"}) == {
        "PentaD": "9,10,11,12"
    }
    # Order of the two keys must not matter.
    assert sp._pentafix({"Penta D": "11,12", "PentaD": "9,10"}) == {
        "PentaD": "9,10,11,12"
    }


def test_pentafix_merges_all_three_spellings():
    merged = sp._pentafix({"PentaE": "14", "Penta E": "16", "Penta_E": "14,18"})
    assert merged == {"PentaE": "14,16,18"}


def test_pentafix_merge_deduplicates():
    assert sp._pentafix({"PentaC": "9,10", "Penta C": "10,9"}) == {"PentaC": "9,10"}


@pytest.mark.parametrize(
    "samp, expected",
    [
        ({"PentaD": "", "Penta D": "11,12"}, {"PentaD": "11,12"}),
        ({"PentaD": "9,10", "Penta D": ""}, {"PentaD": "9,10"}),
        ({"PentaD": "", "Penta D": ""}, {"PentaD": ""}),
    ],
)
def test_pentafix_merge_with_empty_values(samp, expected):
    assert sp._pentafix(samp) == expected


def test_pentafix_merges_colliding_spellings_reverse():
    assert sp._pentafix({"PentaD": "9,10", "Penta_D": "11,12"}, reverse=True) == {
        "Penta D": "9,10,11,12"
    }


def test_pentafix_renames_dataframe_columns():
    """_pentafix is also applied to DataFrames in the CLASTR single-query path."""
    df = pd.DataFrame({"Penta D": ["9,10"], "vWA": ["16"]})
    out = sp._pentafix(df)

    assert list(out.columns) == ["vWA", "PentaD"]
    assert out["PentaD"].tolist() == ["9,10"]
