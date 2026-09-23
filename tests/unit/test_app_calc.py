from strprofiler.shiny_app.calc_functions import _batch_query, _file_query
import pytest

# Identical apart from Amelogenin, so the score only drops when it is scored.
query = {"Amelogenin": "X", "m1": "12", "m2": "14", "m3": "9"}
reference = {"Amelogenin": "X,Y", "m1": "12", "m2": "14", "m3": "9"}
# No valid alleles at all, so there is nothing to score against.
untyped = {"Amelogenin": "", "m1": "OL", "m2": "?", "m3": "NR"}

thresholds = dict(
    three_allele_threshold=3, tan_threshold=80, mas_q_threshold=80, mas_r_threshold=80
)


@pytest.mark.parametrize(
    "use_amel, expected", [(False, "Ref: 100.0"), (True, "Ref: 88.89")]
)
def test_batch_query_honors_amelogenin_switch(use_amel, expected):
    res = _batch_query({"Query": query}, {"Ref": reference}, use_amel, **thresholds)

    assert res.loc[0, "Top Match"] == expected


@pytest.mark.parametrize(
    "use_amel, expected", [(False, "Ref: 100.0"), (True, "Ref: 88.89")]
)
def test_file_query_honors_amelogenin_switch(use_amel, expected):
    res = _file_query({"Query": query, "Ref": reference}, use_amel, **thresholds)

    assert res.loc[0, "Top Match"] == expected


def test_batch_query_skips_unscoreable_reference():
    res = _batch_query(
        {"Query": query}, {"Ref": reference, "Untyped": untyped}, False, **thresholds
    )

    assert res.loc[0, "Top Match"] == "Ref: 100.0"
    assert res.loc[0, "Next Best Match"] == ""


def test_file_query_skips_unscoreable_sample():
    res = _file_query(
        {"Query": query, "Ref": reference, "Untyped": untyped}, False, **thresholds
    )
    res = res.set_index("Sample")

    assert res.loc["Query", "Top Match"] == "Ref: 100.0"
    assert res.loc["Query", "Next Best Match"] == ""
    # Nothing can be scored against the untyped sample, so it has no matches.
    assert res.loc["Untyped", "Top Match"] == ""
