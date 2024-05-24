import rich_click as click
from pathlib import Path
from datetime import datetime
import sys
import pandas as pd
import requests
import json
import strprofiler.utils as utils


@click.command()
@click.option(
    "-sa",
    "--search_algorithm",
    default=1,
    help="""Search algorithm to use in the Clastr query.
            1 - Tanabe, 2 - Masters (vs. query); 3 - Masters (vs. reference)""",
    show_default=True,
    type=int,
)
@click.option(
    "-sm",
    "--scoring_mode",
    default=1,
    help="""Search mode to account for missing alleles in query or reference.
    1 - Non-empty markers, 2 - Query markers, 3 - Reference markers.""",
    show_default=True,
    type=int,
)
@click.option(
    "-sf",
    "--score_filter",
    default=80,
    help="Minimum score to report as potential matches in summary table.",
    show_default=True,
    type=int,
)
@click.option(
    "-mr",
    "--max_results",
    default=200,
    help="Filter defining the maximum number of results to be returned.",
    show_default=True,
    type=int,
)
@click.option(
    "-mm",
    "--min_markers",
    default=8,
    help="Filter defining the minimum number of markers for matches to be reported.",
    show_default=True,
    type=int,
)
@click.option(
    "-sm",
    "--sample_map",
    help="""Path to sample map in csv format for renaming.
              First column should be sample names as given in STR file(s),
              second should be new names to assign. No header.""",
    type=click.Path(),
)
@click.option(
    "-scol",
    "--sample_col",
    help="Name of sample column in STR file(s).",
    default="Sample",
    show_default=True,
    type=str,
)
@click.option(
    "-mcol",
    "--marker_col",
    help="""Name of marker column in STR file(s).
              Only used if format is 'wide'.""",
    default="Marker",
    show_default=True,
    type=str,
)
@click.option(
    "-pfix",
    "--penta_fix",
    help="""Whether to try to harmonize PentaE/D allele spelling.""",
    default=True,
    show_default=True,
    type=bool,
)
@click.option(
    "-amel",
    "--score_amel",
    help="""Use Amelogenin for similarity scoring.""",
    default=False,
    show_default=True,
    type=bool,
)
@click.option(
    "-o",
    "--output_dir",
    default="./STRprofiler",
    help="Path to the output directory.",
    show_default=True,
    type=click.Path(),
)
@click.argument("input_files", required=True, type=click.Path(exists=True), nargs=-1)
@click.version_option()
def clastr_batch_post_request(
    input_files,
    sample_map=None,
    output_dir="./STRprofiler",
    search_algorithm=1,
    scoring_mode=1,
    score_filter=80,
    max_results=200,
    min_markers=8,
    sample_col="Sample Name",
    marker_col="Marker",
    penta_fix=True,
    score_amel=False,
):
    """CLASTR_Query compares STR profiles to the human Cellosaurus knowledge base using the CLASTR REST API.

    :param input_files: List of input STR files in csv, xlsx, tsv, or txt format.
    :type input_files: click.Path

    :param sample_map: Path to sample map in csv format for renaming.
        First column should be sample names as given in STR file(s),
        second should be new names to assign. No header., defaults to None
    :type sample_map: str, optional

    :param output_dir: Path to output directory, defaults to "./STRprofiler"
    :type output_dir: str, optional

    :param search_algorithm: Search algorithm to use in the Clastr query, Options: 1 - Tanabe, 2 - Masters (vs. query); 3 - Masters (vs. reference)
    defaults to 1 (tanabe).
    :type search_algorithm: int

    :param scoring_mode: Search mode to account for missing alleles in query or reference.
    Options: 1 - Non-empty markers, 2 - Query markers, 3 - Reference markers.
    defaults to 1 ( Non-empty markers).
    :type search_algorithm: int

    :param score_filter: Minimum score to report as potential matches in summary table, defaults to 80
    :type score_filter: int, optional

    :param max_results: Filter defining the maximum number of results to be returned.
    Note that in the case of conflicted cell lines, the Best and Worst versions are processed as pairs and only the best
    score is affected by the threshold. Consequently, some Worst cases with a score below the threshold can still be present in the results.
        defaults to 200
    :type mix_threshold: int, optional

    :param min_markers: Filter defining the minimum number of markers for matches to be reported, defaults to 8.
    :type mix_threshold: int, optional

    :param sample_col: Name of sample column in STR file(s), defaults to "Sample Name"
    :type sample_col: str, optional

    :param marker_col: Name of marker column in STR file(s).
        Only used if format is 'wide', defaults to "Marker"
    :type marker_col: str, optional

    :param penta_fix: Whether to try to harmonize PentaE/D allele spelling, defaults to True
    :type penta_fix: bool, optional

    :param score_amel: Use Amelogenin for similarity scoring, defaults to False
    :type score_amel: bool, optional
    """

    # Make output directory and open file for logging.
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d.%H_%M_%S")
    log_file = open(Path(output_dir, "strprofiler.clastrQuery." + dt_string + ".log"), "w")

    print("Search algorithm: " + str(search_algorithm), file=log_file)
    print("Scoring mode: " + str(scoring_mode), file=log_file)
    print("Score filter: " + str(marker_col), file=log_file)
    print("Max results: " + str(max_results), file=log_file)
    print("Min markers: " + str(min_markers), file=log_file)
    print("Sample map: " + str(sample_map), file=log_file)
    print("Sample column: " + str(sample_col), file=log_file)
    print("Marker column: " + str(marker_col), file=log_file)
    print("Penta fix: " + str(penta_fix), file=log_file)
    print("Use amelogenin for scoring: " + str(score_amel) + "\n", file=log_file)
    print("Full command:", file=log_file)

    print(" ".join(sys.argv) + "\n", file=log_file)

    # Check for sample map.
    if sample_map is not None:
        sample_map = pd.read_csv(sample_map, header=None, encoding="unicode_escape")

    # Data ingress.
    query = utils.str_ingress(
        paths=input_files,
        sample_col=sample_col,
        marker_col=marker_col,
        sample_map=sample_map,
        penta_fix=penta_fix,
    ).to_dict(orient="index")

    clastr_query = [(lambda d: d.update(description=key) or d)(val) for (key, val) in query.items()]

    malformed_markers = utils.validate_api_markers(next(iter(clastr_query)).keys())
    if malformed_markers:
        print("Marker(s): {} are incompatible with the CLASTR query. The marker(s) will not be used in the query."
              .format(str(malformed_markers)[1:-1]), file=log_file)
        print("See: https://www.cellosaurus.org/str-search/  for a complete list of compatible marker names", file=log_file)

    url = "https://www.cellosaurus.org/str-search/api/batch/"

    clastr_query = [utils._pentafix(item, reverse=True) for item in clastr_query]
    clastr_query = [dict(item, **{'algorithm': search_algorithm}) for item in clastr_query]
    clastr_query = [dict(item, **{'scoringMode': scoring_mode}) for item in clastr_query]
    clastr_query = [dict(item, **{'scoreFilter': score_filter}) for item in clastr_query]
    clastr_query = [dict(item, **{'includeAmelogenin': score_amel}) for item in clastr_query]
    clastr_query = [dict(item, **{'minMarkers': min_markers}) for item in clastr_query]
    clastr_query = [dict(item, **{'maxResults': max_results}) for item in clastr_query]
    clastr_query = [dict(item, **{'outputFormat': 'xlsx'}) for item in clastr_query]

    print("Querying CLASTR API at: ", url, file=log_file)
    r = requests.post(url, data=json.dumps(clastr_query))

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Request failed with error: '", e, "'", file=log_file)
        print("Request failed with error: '", e, "'")
        return ''

    print("Response from query: ", r.status_code, file=log_file)

    with open(Path(output_dir, "strprofiler.clastrQueryResult." + dt_string + ".xlsx"), "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    print("Results saved: ", Path(output_dir, "strprofiler.clastrQueryResult." + dt_string + ".xlsx"), file=log_file)

    log_file.close()
