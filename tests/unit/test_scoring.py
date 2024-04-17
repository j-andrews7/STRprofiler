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
