import strprofiler as sp
import pytest
from pathlib import Path
import pandas as pd

THIS_DIR = Path(__file__).parent

exp_database = Path(THIS_DIR / "../ExampleSTR_database.csv")
paths = [exp_database]

@pytest.mark.parametrize("paths", [(paths)])
def test_database_ingress(paths):

    # Check that database ingress row and column names are correct when penta fix applied.
    df = sp.str_ingress(
        paths,
        sample_col="Sample Name",
        marker_col="Marker",
        sample_map=None,
        penta_fix=True,
    )

    assert list(df.index) == ["Ref_SampleA", "Ref_SampleB", "Ref_SampleC", "Ref_SampleD", "Ref_SampleE"]
    assert set(df.columns) == set(
        ["marker1", "marker2", "marker4", "PentaD", "PentaE", "AMEL"]
    )

    # Check that dataframe row and column names are correct when  penta fix not applied.
    df = sp.str_ingress(
        paths,
        sample_col="Sample Name",
        marker_col="Marker",
        sample_map=None,
        penta_fix=False,
    )

    assert list(df.index) == ["Ref_SampleA", "Ref_SampleB", "Ref_SampleC", "Ref_SampleD", "Ref_SampleE"]
    assert set(df.columns) == set(
        [
            "marker1",
            "marker2",
            "marker4",
            "Penta D",
            "Penta E",
            "AMEL",
        ]
    )

    # Check the samples are being parsed properly.
    assert list(
        df.loc[
            "Ref_SampleA",
        ]
    ) == ["12,14","12","13","9,10","12,14","X"]
    
    # Check the samples are being parsed properly.
    assert list(
        df.loc[
            "Ref_SampleE",
        ]
    ) == ["14","13","13,15","13","12,15","X,Y"]



# Re-test scoring with database reference df.
query = {
    "marker1": "12,14", 
    "marker2": "12", 
    "marker4": "13", 
    "Penta D": "9,10",
    "Penta E": "12,14",
    "AMEL": "X"
}

reference = pd.DataFrame({
    "Sample": ["Ref_SampleA", "Ref_SampleB", "Ref_SampleE"],
    "marker1": ["12,14", "12,14", "14"],
    "marker2": ["12", "11.3,12", ""],
    "marker4": ["13", "13,15", "13,15"],
    "Penta D": ["9,10", "9,10", "13"],
    "Penta E": ["12,14", "12,14", ""],
    "AMEL": ["X", "X", "X,Y"]
}).set_index('Sample').to_dict(orient="index")

@pytest.mark.parametrize("query, reference, use_amel", [(query, reference, True)])
def test_database_scoring(query, reference, use_amel):

    # Check scoring for query against Ref_SampleA
    scores = sp.score_query(query, reference['Ref_SampleA'], use_amel=use_amel, amel_col="AMEL")
    assert scores["n_shared_markers"] == 6
    assert scores["n_shared_alleles"] == 9
    assert scores["n_query_alleles"] == 9
    assert scores["n_reference_alleles"] == 9
    tan_score = scores["tanabe_score"]
    assert f"{tan_score:.2f}" == "100.00"
    assert scores["masters_query_score"] == 100.0
    mr_score = scores["masters_ref_score"]
    assert f"{mr_score:.2f}" == "100.00"

    # Check scoring for query against Ref_SampleE
    scores = sp.score_query(query, reference['Ref_SampleE'], use_amel=use_amel, amel_col="AMEL")
    assert scores["n_shared_markers"] == 4
    assert scores["n_shared_alleles"] == 3
    assert scores["n_query_alleles"] == 6
    assert scores["n_reference_alleles"] == 6
    tan_score = scores["tanabe_score"]
    assert f"{tan_score:.2f}" == "50.00"
    assert scores["masters_query_score"] == 50.0
    mr_score = scores["masters_ref_score"]
    assert f"{mr_score:.2f}" == "50.00"
