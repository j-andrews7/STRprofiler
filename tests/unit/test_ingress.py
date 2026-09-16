import strprofiler.utils as sp
import pytest
from pathlib import Path
import pandas as pd

THIS_DIR = Path(__file__).parent

exp_long = Path(THIS_DIR / "../ExampleSTR_long.csv")
exp_xlsx = Path(THIS_DIR / "../ExampleSTR.xlsx")
paths = [exp_long, exp_xlsx]

sample_map = pd.read_csv(
    Path(THIS_DIR / "../SampleMap_exp.csv"), header=None, encoding="unicode_escape"
)


@pytest.mark.parametrize("paths, sample_map", [(paths, sample_map)])
def test_ingress_mixed(paths, sample_map):

    # Check that dataframe row and column names are correct when sample map and penta fix applied.
    df = sp.str_ingress(
        paths,
        sample_col="Sample Name",
        marker_col="Marker",
        sample_map=sample_map,
        penta_fix=True,
    )

    assert list(df.index) == ["SampleA", "SampleB", "Sample1", "Sample33"]
    assert set(df.columns) == set(
        ["marker1", "marker2", "marker4", "PentaE", "AMEL", "marker3", "PentaD"]
    )

    # Check that dataframe row and column names are correct when sample map is not supplied.
    df = sp.str_ingress(
        paths,
        sample_col="Sample Name",
        marker_col="Marker",
        sample_map=None,
        penta_fix=True,
    )

    assert list(df.index) == ["SampleA", "SampleB", "Sample1", "Sample3"]
    assert set(df.columns) == set(
        ["marker1", "marker2", "marker4", "PentaE", "AMEL", "marker3", "PentaD"]
    )

    # Check that dataframe row and column names are correct when  penta fix not applied.
    df = sp.str_ingress(
        paths,
        sample_col="Sample Name",
        marker_col="Marker",
        sample_map=sample_map,
        penta_fix=False,
    )

    assert list(df.index) == ["SampleA", "SampleB", "Sample1", "Sample33"]
    assert set(df.columns) == set(
        [
            "marker1",
            "marker2",
            "marker4",
            "Penta D",
            "Penta E",
            "AMEL",
            "marker3",
            "PentaD",
        ]
    )

    # Check the samples are being parsed properly.
    assert list(
        df.loc["SampleA"]
    ) == ["12,14", "12", "13", "9,10", "12,14", "X", "", ""]

    # Check the samples are being parsed properly.
    assert list(
        df.loc["Sample33"]
    ) == ["12,18,19", "20,25,29", "", "", "10,13,18", "X,Y", "10,11,16", "10,11,12"]


app_db = Path(THIS_DIR / "../Example_app_database.csv")


def test_ingress_keeps_metadata_columns():
    """Center/Passage are carried through ingress for reporting."""
    df = sp.str_ingress([app_db], sample_col="Sample", penta_fix=True)

    assert "Center" in df.columns
    assert "Passage" in df.columns
    assert df.loc["Sample_A", "Center"] == "JAX"
    assert df.loc["Sample_A", "Passage"] == "P0"


def test_ingress_metadata_not_scored():
    """Two samples sharing only Center/Passage must not score as a partial match."""
    samps = sp.str_ingress([app_db], sample_col="Sample", penta_fix=True).to_dict(
        orient="index"
    )

    assert samps["Sample_A"]["Center"] == samps["Sample_B"]["Center"]
    assert samps["Sample_A"]["Passage"] == samps["Sample_B"]["Passage"]

    scores = sp.score_query(samps["Sample_A"], samps["Sample_B"], amel_col="Amelogenin")

    # 8 columns, minus Center/Passage, minus Amelogenin (not scored by default).
    assert scores["n_shared_markers"] == 5
    assert scores["n_shared_alleles"] == 0
    assert scores["tanabe_score"] == 0.0


def test_ingress_merges_mixed_penta_spellings(tmp_path):
    """A sample typed under both Penta spellings must keep both calls."""
    path = tmp_path / "mixed_penta.csv"
    path.write_text(
        "Sample,marker1,Penta D,PentaD\n" 'SampleA,"12,14","9,10","11,12"\n',
        encoding="utf-8",
    )

    df = sp.str_ingress([path], sample_col="Sample", penta_fix=True)

    assert "Penta D" not in df.columns
    assert df.loc["SampleA", "PentaD"] == "9,10,11,12"


def test_ingress_duplicate_sample_names_raise(tmp_path):
    path = tmp_path / "dupes.csv"
    path.write_text(
        "Sample,marker1\nSampleA,12\nSampleA,14\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate"):
        sp.str_ingress([path], sample_col="Sample")


def test_ingress_discards_non_numeric_alleles(tmp_path):
    """Off-ladder and ambiguous calls must not reach the allele dicts."""
    path = tmp_path / "off_ladder.csv"
    path.write_text(
        "Sample,marker1,marker2,marker3,AMEL\n"
        'SampleA,"12,OL","?","OL,?","X,Y"\n'
        'SampleB,"12,14","13","12","X"\n',
        encoding="utf-8",
    )

    df = sp.str_ingress([path], sample_col="Sample")

    assert df.loc["SampleA", "marker1"] == "12"
    assert df.loc["SampleA", "marker2"] == ""
    assert df.loc["SampleA", "marker3"] == ""
    # Amelogenin is non-numeric but a real call.
    assert df.loc["SampleA", "AMEL"] == "X,Y"

    samps = df.to_dict(orient="index")
    scores = sp.score_query(samps["SampleA"], samps["SampleB"])

    # Only marker1 is comparable; marker2/marker3 held no valid alleles for SampleA.
    assert scores["n_shared_markers"] == 1
    assert scores["n_query_alleles"] == 1
    assert scores["n_shared_alleles"] == 1


def test_ingress_preserves_metadata_text(tmp_path):
    """Metadata is not allele data, so it must not be parsed as alleles."""
    path = tmp_path / "meta.csv"
    path.write_text(
        "Sample,Center,Passage,marker1\nSampleA,JAX,P0,\"12,OL\"\n",
        encoding="utf-8",
    )

    df = sp.str_ingress([path], sample_col="Sample")

    assert df.loc["SampleA", "Center"] == "JAX"
    assert df.loc["SampleA", "Passage"] == "P0"
    assert df.loc["SampleA", "marker1"] == "12"


def test_ingress_custom_metadata_cols(tmp_path):
    """A caller may declare their own non-marker columns."""
    path = tmp_path / "custom_meta.csv"
    path.write_text(
        "Sample,Tissue,marker1\nSampleA,Brain,\"12,14\"\n",
        encoding="utf-8",
    )

    df = sp.str_ingress([path], sample_col="Sample", metadata_cols=["Tissue"])
    assert df.loc["SampleA", "Tissue"] == "Brain"

    # Without declaring it, the free-text value is not a valid allele.
    df = sp.str_ingress([path], sample_col="Sample")
    assert df.loc["SampleA", "Tissue"] == ""
