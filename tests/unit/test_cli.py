import pandas as pd
import pytest
import warnings
from click.testing import CliRunner
from importlib.metadata import version
from pathlib import Path

from strprofiler.cli import cli

THIS_DIR = Path(__file__).parent
exp_long = Path(THIS_DIR / "../ExampleSTR_long.csv")
exp_1samp = Path(THIS_DIR / "../ExampleSTR_long_1samp.csv")
exp_database = Path(THIS_DIR / "../ExampleSTR_database.csv")


def _summary(output_dir):
    summaries = list(Path(output_dir).glob("full_summary.strprofiler.*.csv"))
    assert len(summaries) == 1
    return pd.read_csv(summaries[0]).fillna("")


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.parametrize(
    "args",
    [
        ["--version"],
        ["compare", "--version"],
        ["clastr", "--version"],
        ["app", "--version"],
    ],
)
def test_version_reports_strprofiler_version(runner, args):
    """rich_click defeats click's frame-based package detection.

    Without an explicit package_name, every command reported rich-click's version
    instead of strprofiler's.
    """
    result = runner.invoke(cli, args, prog_name="strprofiler")

    assert result.exit_code == 0, result.output
    assert result.output.strip() == f"strprofiler, version {version('strprofiler')}"
    assert version("strprofiler") != version("rich-click")


@pytest.mark.parametrize(
    "name, command",
    [("cli", cli)] + sorted(cli.commands.items()),
)
def test_no_duplicate_option_flags(name, command):
    """A flag declared twice silently shadows one of its options."""
    seen = {}
    for param in command.params:
        for opt in list(param.opts) + list(param.secondary_opts):
            assert opt not in seen, (
                f"{name}: {opt} is shared by '{seen[opt]}' and '{param.name}'"
            )
            seen[opt] = param.name


def test_clastr_scoring_mode_and_sample_map_flags():
    """`-sm` belonged to --sample_map, matching `compare`, so --scoring_mode moved to -scm."""
    params = {param.name: param.opts for param in cli.commands["clastr"].params}

    assert "-scm" in params["scoring_mode"]
    assert "-sm" not in params["scoring_mode"]
    assert "-sm" in params["sample_map"]


@pytest.mark.parametrize("name", ["compare", "clastr"])
def test_score_amel_is_a_flag(name):
    """`-amel` takes no value; it previously required e.g. `-amel True`."""
    params = {param.name: param for param in cli.commands[name].params}

    assert params["score_amel"].is_flag
    assert params["score_amel"].default is False


@pytest.mark.parametrize("name", sorted(cli.commands))
def test_help_emits_no_parameter_warnings(runner, name):
    """click warns on duplicate flags while building the parser."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        result = runner.invoke(cli, [name, "--help"], prog_name="strprofiler")

    assert result.exception is None, result.exception
    assert result.exit_code == 0, result.output


def test_clastr_help_lists_both_flags(runner):
    result = runner.invoke(cli, ["clastr", "--help"], prog_name="strprofiler")

    assert result.exit_code == 0, result.output
    assert "-scm" in result.output
    assert "-sm" in result.output


def test_compare_against_database(runner, tmp_path):
    result = runner.invoke(
        cli,
        [
            "compare",
            "-db", str(exp_database),
            "-scol", "Sample Name",
            "-o", str(tmp_path),
            str(exp_long),
        ],
    )

    assert result.exit_code == 0, result.output

    summary = _summary(tmp_path)
    assert summary["Sample"].tolist() == ["SampleA", "SampleB"]
    assert summary.loc[0, "top_hit"] == "Ref_SampleA: 100.0"
    assert summary.loc[0, "next_best"] == "Ref_SampleB: 88.89"


def test_compare_single_profile_database_matching_query(runner, tmp_path):
    """The only database profile is the query itself, so no comparisons remain.

    This previously raised an IndexError in make_summary().
    """
    result = runner.invoke(
        cli,
        [
            "compare",
            "-db", str(exp_1samp),
            "-scol", "Sample Name",
            "-o", str(tmp_path),
            str(exp_1samp),
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.exception is None

    summary = _summary(tmp_path)
    assert summary["Sample"].tolist() == ["SampleA"]
    assert summary.loc[0, "top_hit"] == ""
    assert summary.loc[0, "next_best"] == ""
    assert summary.loc[0, "tanabe_matches"] == ""


def test_compare_single_input_without_database_exits_cleanly(runner, tmp_path):
    result = runner.invoke(
        cli,
        [
            "compare",
            "-scol", "Sample Name",
            "-o", str(tmp_path),
            str(exp_1samp),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "no database for comparison" in result.output
    assert list(Path(tmp_path).glob("full_summary.strprofiler.*.csv")) == []


def test_compare_writes_html_summary(runner, tmp_path):
    result = runner.invoke(
        cli,
        [
            "compare",
            "-scol", "Sample Name",
            "-o", str(tmp_path),
            str(exp_long),
        ],
    )

    assert result.exit_code == 0, result.output

    html = list(Path(tmp_path).glob("full_summary.strprofiler.*.html"))
    assert len(html) == 1
    assert "STRprofiler Results" in html[0].read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "score_amel, expected", [([], "Sample_B: 100.0"), (["-amel"], "Sample_B: 88.89")]
)
def test_compare_honors_amel_col(runner, tmp_path, score_amel, expected):
    """A custom --amel_col is only scored when --score_amel is passed.

    The option was previously ignored, so this column was always scored.
    """
    input_file = tmp_path / "amel.csv"
    input_file.write_text(
        "Sample,Amelogenin,m1,m2,m3\n"
        "Sample_A,X,12,14,9\n"
        "Sample_B,\"X,Y\",12,14,9\n"
    )
    out_dir = tmp_path / "out"

    result = runner.invoke(
        cli,
        ["compare", "-acol", "Amelogenin", *score_amel, "-o", str(out_dir), str(input_file)],
    )

    assert result.exit_code == 0, result.output
    summary = _summary(out_dir)
    assert summary.loc[summary["Sample"] == "Sample_A", "top_hit"].item() == expected
