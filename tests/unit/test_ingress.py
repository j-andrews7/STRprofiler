import strprofiler as sp
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
        df.loc[
            "SampleA",
        ]
    ) == ["12,14", "12", "13", "9,10", "12,14", "X", "", ""]
    
    # Check the samples are being parsed properly.
    assert list(
        df.loc[
            "Sample33",
        ]
    ) == ["12,18,19", "20,25,29", "", "", "10,13,18", "X,Y", "10,11,16", "10,11,12"]
