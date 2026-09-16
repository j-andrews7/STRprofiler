import strprofiler.utils as sp
import pytest

inp = "10.0,10,13,13.0,14,14 "


@pytest.mark.parametrize("x", [(inp)])
def test_cleaning(x):
    assert sp._clean_element(x) == "10,13,14"


@pytest.mark.parametrize(
    "x, expected",
    [
        # A trailing comma must not survive as an empty allele.
        ("12,", "12"),
        (",12", "12"),
        ("12, ,14", "12,14"),
        ("12,,14", "12,14"),
        ("", ""),
        (",", ""),
        (" ", ""),
        # Non-numeric alleles are kept and sorted after numeric ones.
        ("X,Y,", "X,Y"),
        ("12,X,", "12,X"),
    ],
)
def test_cleaning_empty_tokens(x, expected):
    assert sp._clean_element(x) == expected


@pytest.mark.parametrize(
    "x, expected",
    [
        # Off-ladder and ambiguous calls are not comparable alleles.
        ("12,OL", "12"),
        ("12,?", "12"),
        ("OL", ""),
        ("?", ""),
        ("12,OL,14", "12,14"),
        ("12,NR,ND,NA,-", "12"),
        ("OL,?", ""),
        # float() accepts these, but they are not alleles.
        ("12,nan", "12"),
        ("12,inf", "12"),
        ("12,-inf", "12"),
        # Amelogenin sex markers are real calls and must survive.
        ("X,Y", "X,Y"),
        ("X,OL", "X"),
        ("12,X,OL,?", "12,X"),
        # Case is normalized so x and X are not counted as two alleles.
        ("x,y", "X,Y"),
        ("X,x", "X"),
    ],
)
def test_cleaning_discards_non_numeric_alleles(x, expected):
    assert sp._clean_element(x) == expected


def test_non_numeric_alleles_constant():
    """The keep-list is the amelogenin sex markers only."""
    assert sp.NON_NUMERIC_ALLELES == ("X", "Y")


def test_clean_element_trailing_comma_not_scored():
    """A trailing comma previously inflated the query allele count."""
    scores = sp.score_query({"m1": sp._clean_element("12,")}, {"m1": "12"})

    assert scores["n_query_alleles"] == 1
    assert scores["n_reference_alleles"] == 1
    assert scores["n_shared_alleles"] == 1
    assert scores["tanabe_score"] == 100.0
