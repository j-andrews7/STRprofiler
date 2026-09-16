import strprofiler.utils as sp
import pytest

query = {
    "mark1": "11,12", 
    "mark2": "", 
    "mark3": "13", 
    "mark4": "5,5,7", 
    "AMEL": "X"
}

reference = {
    "mark1": "11,12",
    "mark2": "3",
    "mark3": "13,14",
    "mark4": "5,7",
    "AMEL": "X",
}


@pytest.mark.parametrize("query, reference, use_amel", [(query, reference, False)])
def test_scoring(query, reference, use_amel):
    scores = sp.score_query(query, reference, use_amel=use_amel, amel_col="AMEL")

    assert scores["n_shared_markers"] == 3
    assert scores["n_shared_alleles"] == 5
    assert scores["n_query_alleles"] == 5
    assert scores["n_reference_alleles"] == 6
    tan_score = scores["tanabe_score"]
    assert f"{tan_score:.2f}" == "90.91"
    assert scores["masters_query_score"] == 100.0
    mr_score = scores["masters_ref_score"]
    assert f"{mr_score:.2f}" == "83.33"


@pytest.mark.parametrize("query, reference, use_amel", [(query, reference, True)])
def test_scoring_amel(query, reference, use_amel):
    scores = sp.score_query(query, reference, use_amel=use_amel, amel_col="AMEL")

    assert scores["n_shared_markers"] == 4
    assert scores["n_shared_alleles"] == 6
    assert scores["n_query_alleles"] == 6
    assert scores["n_reference_alleles"] == 7
    tan_score = scores["tanabe_score"]
    assert f"{tan_score:.2f}" == "92.31"
    assert scores["masters_query_score"] == 100.0
    mr_score = scores["masters_ref_score"]
    assert f"{mr_score:.2f}" == "85.71"


# Metadata columns are not STR markers and must never contribute to a score.
meta_query = {"Center": "JAX", "Passage": "P0", "vWA": "16,18"}
meta_reference = {"Center": "JAX", "Passage": "P0", "vWA": "11,12"}


def test_scoring_ignores_metadata_columns():
    """Shared Center/Passage previously inflated every count and the scores."""
    scores = sp.score_query(meta_query, meta_reference)

    assert scores["n_shared_markers"] == 1
    assert scores["n_shared_alleles"] == 0
    assert scores["n_query_alleles"] == 2
    assert scores["n_reference_alleles"] == 2
    assert scores["tanabe_score"] == 0.0
    assert scores["masters_query_score"] == 0.0
    assert scores["masters_ref_score"] == 0.0


def test_scoring_metadata_does_not_change_score():
    """Samples from the same center must score the same as samples from different ones."""
    shared = sp.score_query(meta_query, meta_reference)
    unshared = sp.score_query(
        meta_query, dict(meta_reference, Center="Other", Passage="P9")
    )

    assert shared == unshared


def test_scoring_metadata_cols_override():
    """A caller may supply their own non-marker column names."""
    scores = sp.score_query(
        {"Site": "JAX", "vWA": "16,18"},
        {"Site": "JAX", "vWA": "11,12"},
        metadata_cols=["Site"],
    )

    assert scores["n_shared_markers"] == 1
    assert scores["tanabe_score"] == 0.0


def test_scoring_metadata_cols_disabled():
    """Passing an empty collection restores scoring of every column."""
    scores = sp.score_query(
        {"Center": "12", "vWA": "16,18"},
        {"Center": "12", "vWA": "11,12"},
        metadata_cols=[],
    )

    assert scores["n_shared_markers"] == 2
    assert scores["n_shared_alleles"] == 1


def test_scoring_metadata_text_never_counts_as_alleles():
    """Even with the metadata exclusion off, free-text values are not valid alleles."""
    scores = sp.score_query(meta_query, meta_reference, metadata_cols=[])

    assert scores["n_shared_markers"] == 1
    assert scores["n_shared_alleles"] == 0
    assert scores["tanabe_score"] == 0.0


# Off-ladder, ambiguous and other non-numeric calls carry no comparable allele.
@pytest.mark.parametrize("junk", ["OL", "?", "NR", "ND", "NA", "-", "n/a", "nan", "inf"])
def test_scoring_discards_non_numeric_alleles(junk):
    scores = sp.score_query({"m1": f"12,{junk}"}, {"m1": "12"})

    assert scores["n_query_alleles"] == 1
    assert scores["n_reference_alleles"] == 1
    assert scores["n_shared_alleles"] == 1
    assert scores["tanabe_score"] == 100.0


def test_scoring_marker_with_only_invalid_alleles_is_dropped():
    """A marker typed only as off-ladder is not a shared marker."""
    scores = sp.score_query({"m1": "12", "m2": "OL"}, {"m1": "12", "m2": "OL"})

    assert scores["n_shared_markers"] == 1
    assert scores["n_query_alleles"] == 1
    assert scores["tanabe_score"] == 100.0


def test_scoring_keeps_amelogenin_sex_markers():
    """X/Y are real calls and must survive the non-numeric filter."""
    scores = sp.score_query(
        {"AMEL": "X,Y", "m1": "12"}, {"AMEL": "X,Y", "m1": "12"}, use_amel=True
    )

    assert scores["n_shared_markers"] == 2
    assert scores["n_shared_alleles"] == 3
    assert scores["tanabe_score"] == 100.0


def test_scoring_normalizes_allele_formatting():
    """"12.0", " 12" and "12" are the same allele."""
    scores = sp.score_query({"m1": "12.0, 14"}, {"m1": "12,14"})

    assert scores["n_query_alleles"] == 2
    assert scores["n_shared_alleles"] == 2
    assert scores["tanabe_score"] == 100.0
