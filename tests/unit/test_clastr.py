import strprofiler.utils as sp
import strprofiler.shiny_app.clastr_api as clastr_api
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

    url = "https://www.cellosaurus.org/str-search/api/batch/%"

    r = requests.post(url, data=json.dumps(clastr_query))

    assert r.status_code == 404

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        assert e


class _FakeErrorResponse:
    """Minimal response that makes the CLASTR helpers bail out after posting."""

    def raise_for_status(self):
        raise requests.exceptions.HTTPError("503 Server Error")


@pytest.fixture
def captured_post(monkeypatch):
    """Capture the payload posted to CLASTR without hitting the network."""
    captured = {}

    def _fake_post(url, data=None, **kwargs):
        captured["url"] = url
        captured["payload"] = json.loads(data)
        return _FakeErrorResponse()

    monkeypatch.setattr(clastr_api.requests, "post", _fake_post)
    return captured


batch_query = [
    {
        "description": "Sample_A",
        "Amelogenin": "X,Y",
        "CSF1PO": "12",
        "vWA": "18",
    }
]

single_query = {"Amelogenin": "X,Y", "CSF1PO": "12", "vWA": "18"}


@pytest.mark.parametrize(
    "query_filter, expected_algorithm",
    [("Tanabe", 1), ("Masters Query", 2), ("Masters Reference", 3)],
)
def test_clastr_batch_query_algorithm(captured_post, query_filter, expected_algorithm):
    """Batch queries previously sent algorithm 2 for Masters (vs. reference)."""
    result = clastr_api._clastr_batch_query(
        [dict(item) for item in batch_query], query_filter, False, 80
    )

    assert captured_post["payload"][0]["algorithm"] == expected_algorithm
    assert captured_post["payload"][0]["scoreFilter"] == 80
    assert captured_post["payload"][0]["includeAmelogenin"] is False
    # HTTP failures are surfaced as a single-column error frame.
    assert list(result.columns) == ["Error"]


@pytest.mark.parametrize(
    "query_filter, expected_algorithm",
    [("Tanabe", 1), ("Masters Query", 2), ("Masters Reference", 3)],
)
def test_clastr_single_query_algorithm(captured_post, query_filter, expected_algorithm):
    """The single-query path must agree with the batch path."""
    result = clastr_api._clastr_query(dict(single_query), query_filter, False, 80)

    assert captured_post["payload"]["algorithm"] == expected_algorithm
    assert captured_post["payload"]["scoreFilter"] == 80
    assert list(result.columns) == ["Error"]


def test_clastr_batch_and_single_agree_on_algorithm(monkeypatch):
    """Lock the two code paths together so they cannot drift apart again."""
    seen = []

    def _fake_post(url, data=None, **kwargs):
        seen.append(json.loads(data))
        return _FakeErrorResponse()

    monkeypatch.setattr(clastr_api.requests, "post", _fake_post)

    for query_filter in ["Tanabe", "Masters Query", "Masters Reference"]:
        clastr_api._clastr_query(dict(single_query), query_filter, False, 80)
        clastr_api._clastr_batch_query(
            [dict(item) for item in batch_query], query_filter, False, 80
        )

    for single, batch in zip(seen[::2], seen[1::2]):
        assert single["algorithm"] == batch[0]["algorithm"]


def test_clastr_batch_query_pentafix_applied(captured_post):
    """Compact Penta spellings are expanded to the names CLASTR expects."""
    clastr_api._clastr_batch_query(
        [{"description": "Sample_A", "PentaD": "9,10", "PentaE": "12,14"}],
        "Tanabe",
        False,
        80,
    )

    posted = captured_post["payload"][0]
    assert posted["Penta D"] == "9,10"
    assert posted["Penta E"] == "12,14"
    assert "PentaD" not in posted


def test_validate_api_markers_ignores_metadata_columns():
    """Center/Passage are recognised non-marker columns, not malformed markers."""
    markers = ["Amelogenin", "vWA", "Center", "Passage", "description"]

    assert sp.validate_api_markers(markers) == []
    assert sp.validate_api_markers(markers + ["NotAMarker"]) == ["NotAMarker"]
