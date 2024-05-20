import strprofiler.utils as sp
import pytest
from pathlib import Path
import requests
import json
import types

THIS_DIR = Path(__file__).parent

exp_clastr = Path(THIS_DIR / "../Example_clastr_input.csv")
paths = [exp_clastr]


@pytest.mark.parametrize("paths", [(paths)])
def test_clastr(paths):

    # Check that dataframe row and column names are correct when sample map and penta fix applied.
    df = sp.str_ingress(
        paths,
        sample_col="Sample",
        marker_col="Marker",
        sample_map=None,
        penta_fix=True,
    )

    assert list(df.index) == ["Sample_A", "Sample_B", "Sample_C"]
    assert set(df.columns) == set(
        ["Amel", "CSF1PO", "D2S1338", "D3S1358", "D5S818", "D7S820", "D8S1179",
         "D13S317", "D16S539", "D18S51", "D19S433", "D21S11", "FGA",
         "PentaD", "PentaE", "TH01", "TPOX", "vWA"]
    )

    clastr_query = [(lambda d: d.update(description=key) or d)(val) for (key, val) in df.to_dict(orient="index").items()]

    url = "https://www.cellosaurus.org/str-search/api/batch/"

    clastr_query = [sp._pentafix(item, reverse=True) for item in clastr_query]
    clastr_query = [dict(item, **{'algorithm': 1}) for item in clastr_query]
    clastr_query = [dict(item, **{'scoringMode': 1}) for item in clastr_query]
    clastr_query = [dict(item, **{'scoreFilter': 80}) for item in clastr_query]
    clastr_query = [dict(item, **{'includeAmelogenin': False}) for item in clastr_query]
    clastr_query = [dict(item, **{'minMarkers': 8}) for item in clastr_query]
    clastr_query = [dict(item, **{'maxResults': 200}) for item in clastr_query]
    clastr_query = [dict(item, **{'outputFormat': 'xlsx'}) for item in clastr_query]

    r = requests.post(url, data=json.dumps(clastr_query))

    assert r.status_code == 200

    assert isinstance(r.iter_content(chunk_size=128), types.GeneratorType)
