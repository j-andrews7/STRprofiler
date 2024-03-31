import pandas as pd
import rich_click as click
from pathlib import Path
from datetime import datetime
from collections import OrderedDict
from math import nan
import sys
from shiny import run_app
from strprofiler.app.app import create_app
import strprofiler.utils as utils


@click.command()
@click.option(
    "-tanth",
    "--tan_threshold",
    default=80,
    help="Minimum Tanabe score to report as potential matches in summary table.",
    show_default=True,
    type=float,
)
@click.option(
    "-masqth",
    "--mas_q_threshold",
    default=80,
    help="Minimum Masters (vs. query) score to report as potential matches in summary table.",
    show_default=True,
    type=float,
)
@click.option(
    "-masrth",
    "--mas_r_threshold",
    default=80,
    help="Minimum Masters (vs. reference) score to report as potential matches in summary table.",
    show_default=True,
    type=float,
)
@click.option(
    "-mix",
    "--mix_threshold",
    default=3,
    help="Number of markers with >= 2 alleles allowed before a sample is flagged for potential mixing.",
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
    "-db",
    "--database",
    help="Path to an STR database file in csv, xlsx, tsv, or txt format.",
    type=click.Path(exists=True),
)
@click.option(
    "-acol",
    "--amel_col",
    help="Name of Amelogenin column in STR file(s).",
    default="AMEL",
    show_default=True,
    type=str,
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
def strprofiler(
    input_files,
    sample_map=None,
    database=None,
    output_dir="./STRprofiler",
    tan_threshold=80,
    mas_q_threshold=80,
    mas_r_threshold=80,
    mix_threshold=4,
    amel_col="AMEL",
    sample_col="Sample Name",
    marker_col="Marker",
    penta_fix=True,
    score_amel=False,
):
    """STRprofiler compares STR profiles to each other.

    :param input_files: List of input STR files in csv, xlsx, tsv, or txt format.
    :type input_files: click.Path
    :param sample_map: Path to sample map in csv format for renaming.
        First column should be sample names as given in STR file(s),
        second should be new names to assign. No header., defaults to None
    :type sample_map: str, optional
    :param database: Path to a database file in csv, xlsx, tsv, or txt format.
        If provided, input files are quried against this database, defaults to None
    :type database: str, optional
    :param output_dir: Path to output directory, defaults to "./STRprofiler"
    :type output_dir: str, optional
    :param tan_threshold: Minimum Tanabe score to report as potential matches in summary table, defaults to 80
    :type tan_threshold: int, optional
    :param mas_q_threshold: Minimum Masters (vs. query) score to report as potential matches in summary table, defaults to 80
    :type mas_q_threshold: int, optional
    :param mas_r_threshold: Minimum Masters (vs. reference) score to report as potential matches in summary table,
        defaults to 80
    :type mas_r_threshold: int, optional
    :param mix_threshold: Number of markers with >= 2 alleles allowed before a sample is flagged for potential mixing,
        defaults to 4
    :type mix_threshold: int, optional
    :param amel_col: Name of Amelogenin column in STR file(s), defaults to "AMEL"
    :type amel_col: str, optional
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
    log_file = open(Path(output_dir, "strprofiler." + dt_string + ".log"), "w")

    print("Tanabe threshold: " + str(tan_threshold), file=log_file)
    print("Masters (vs. query) threshold: " + str(mas_q_threshold), file=log_file)
    print("Masters (vs. reference) threshold: " + str(mas_r_threshold), file=log_file)
    print("Mix threshold: " + str(mix_threshold), file=log_file)
    print("Sample map: " + str(sample_map), file=log_file)
    print("Amelogenin column: " + amel_col, file=log_file)
    print("Sample column: " + sample_col, file=log_file)
    print("Marker column: " + marker_col, file=log_file)
    print("Penta fix: " + str(penta_fix), file=log_file)
    print("Use amelogenin for scoring: " + str(score_amel) + "\n", file=log_file)
    print("Full command:", file=log_file)

    print(" ".join(sys.argv) + "\n", file=log_file)

    print("Comparisons:", file=log_file)

    # Check for sample map.
    if sample_map is not None:
        sample_map = pd.read_csv(sample_map, header=None, encoding="unicode_escape")

    # Data ingress.
    df = utils.str_ingress(
        paths=input_files,
        sample_col=sample_col,
        marker_col=marker_col,
        sample_map=sample_map,
        penta_fix=penta_fix,
    )

    samps = df.to_dict(orient="index")
    summaries = []

    # Database ingress, if present
    # Set 'reference' for subsequent query to either database or inputs all to all
    if database is not None:
        # load_database(database)
        df_db = utils.str_ingress(
            paths=[database],
            sample_col=sample_col,
            marker_col=marker_col,
            sample_map=None,
            penta_fix=penta_fix,
        )
        reference_samps = df_db.to_dict(orient="index")
    else:
        reference_samps = samps

    # Iterate through samples and compare to each other.
    # comparing either to inputs to database or inputs all to all
    for s in samps.keys():
        q = samps[s]
        # Check for sample mixing.
        mixed = utils.mixing_check(alleles=q, three_allele_threshold=mix_threshold)

        q_out = {
            "Sample": s,
            "mixed": mixed,
            "query_sample": True,
            "n_shared_markers": nan,
            "n_shared_alleles": nan,
            "n_query_alleles": nan,
            "n_reference_alleles": nan,
            "tanabe_score": nan,
            "masters_query_score": nan,
            "masters_ref_score": nan,
        }
        q_out.update(q)

        # Put query sample first.
        samp_comps = [q_out]

        for sa in reference_samps.keys():
            if sa != s:
                r = reference_samps[sa]
                print("Comparing " + s + " to " + sa, file=log_file)
                scores = utils.score_query(query=q, reference=r, use_amel=score_amel)

                # Create dict of scores for each sample comparison.
                samp_out = OrderedDict({"Sample": sa})
                samp_out.update(scores)
                samp_out.update(r)

                samp_comps.append(samp_out)

        # Create DataFrame of scores for each sample comparison.
        full_samp_out = pd.DataFrame(samp_comps)
        full_samp_out.sort_values(
            by="tanabe_score", ascending=False, inplace=True, na_position="first"
        )

        # Write sample-specific output.
        full_samp_out.to_csv(
            Path(output_dir, s + ".strprofiler." + dt_string + ".csv"), index=False
        )

        # Generate summary of scores for given sample.
        summ = utils.make_summary(
            samp_df=full_samp_out,
            alleles=q,
            tan_threshold=tan_threshold,
            mas_q_threshold=mas_q_threshold,
            mas_r_threshold=mas_r_threshold,
            mixed=mixed,
            s_name=s,
        )

        summaries.append(summ)

    summaries = pd.DataFrame(summaries)

    # Write summary output.
    summaries.to_csv(
        Path(output_dir, "full_summary.strprofiler." + dt_string + ".csv"), index=False
    )

    # Write html summary output.
    html_df = utils._make_html(summaries)
    open(
        Path(output_dir, "full_summary.strprofiler." + dt_string + ".html"), "w"
    ).write(html_df)

    log_file.close()


@click.command()
@click.option(
    "-db",
    "--database",
    help="Path to an STR database file in csv, xlsx, tsv, or txt format.",
    type=click.Path(exists=True),
)
@click.version_option()
def app(database=None):
    """STRprofiler shiny application for interactive comparisons & querying of STR profiles.

    :param database: Path to a database file in csv, xlsx, tsv, or txt format. If provided, will be loaded into the app, defaults to None
    :type database: str, optional
    """
    str_app = create_app(db=database)
    run_app(str_app)
