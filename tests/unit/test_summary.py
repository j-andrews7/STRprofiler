import strprofiler.utils as sp
import pandas as pd
import pytest
from math import nan

alleles = {"marker1": "12,14", "marker2": "12"}


def _samp_df(rows):
    """Build a sample-specific output frame, query row first, as strprofiler does."""
    query_row = {
        "Sample": "Query",
        "tanabe_score": nan,
        "masters_query_score": nan,
        "masters_ref_score": nan,
    }
    return pd.DataFrame([query_row] + rows)


def test_make_summary_single_row():
    """A one-profile database that only holds the query leaves nothing to compare."""
    summ = sp.make_summary(
        _samp_df([]), alleles, 80, 80, 80, False, "Query"
    )

    assert summ["top_hit"] == ""
    assert summ["next_best"] == ""
    assert summ["tanabe_matches"] == ""
    assert summ["Sample"] == "Query"
    assert summ["mixed"] is False
    assert summ["marker1"] == "12,14"


def test_make_summary_two_rows():
    summ = sp.make_summary(
        _samp_df(
            [
                {
                    "Sample": "Ref_A",
                    "tanabe_score": 95.0,
                    "masters_query_score": 90.0,
                    "masters_ref_score": 85.0,
                }
            ]
        ),
        alleles,
        80,
        80,
        80,
        False,
        "Query",
    )

    assert summ["top_hit"] == "Ref_A: 95.0"
    assert summ["next_best"] == ""
    assert summ["tanabe_matches"] == "Ref_A: 95.0"
    assert summ["masters_query_matches"] == "Ref_A: 90.0"
    assert summ["masters_ref_matches"] == "Ref_A: 85.0"


def test_make_summary_three_rows():
    summ = sp.make_summary(
        _samp_df(
            [
                {
                    "Sample": "Ref_A",
                    "tanabe_score": 95.0,
                    "masters_query_score": 90.0,
                    "masters_ref_score": 85.0,
                },
                {
                    "Sample": "Ref_B",
                    "tanabe_score": 72.555,
                    "masters_query_score": 60.0,
                    "masters_ref_score": 60.0,
                },
            ]
        ),
        alleles,
        80,
        80,
        80,
        False,
        "Query",
    )

    assert summ["top_hit"] == "Ref_A: 95.0"
    assert summ["next_best"] == "Ref_B: 72.56"
    # Only Ref_A clears the thresholds.
    assert summ["tanabe_matches"] == "Ref_A: 95.0"
    assert summ["masters_query_matches"] == "Ref_A: 90.0"


@pytest.mark.parametrize("mixed", [True, False])
def test_make_summary_passes_through_flags(mixed):
    summ = sp.make_summary(_samp_df([]), alleles, 80, 80, 80, mixed, "Query")

    assert summ["mixed"] is mixed
    assert list(summ.keys())[:7] == [
        "Sample",
        "mixed",
        "top_hit",
        "next_best",
        "tanabe_matches",
        "masters_query_matches",
        "masters_ref_matches",
    ]
