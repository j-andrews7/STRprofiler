import pandas as pd
import numpy as np
from datetime import datetime
from importlib.metadata import version
import sys
from pathlib import Path
from collections import OrderedDict


def _clean_element(x):
    """
    Takes a string of alleles, removes duplicates, trims trailing .0, and returns a cleaned string.
    Sorts elements in ascending numeric order, with strings coming after numbers.
    """
    elements = [s.strip() for s in x.split(",")]

    # Separate elements into numeric and string categories
    numeric_elements = []
    string_elements = []
    for e in elements:
        try:
            numeric_elements.append(float(e))
        except ValueError:
            string_elements.append(e)

    # Remove duplicates and sort numeric elements in ascending order
    numeric_elements = sorted(list(set(numeric_elements)))
    string_elements = sorted(list(set(string_elements)))

    # Convert numeric elements back to string and remove trailing .0 if needed
    numeric_elements = [str(e)[:-2] if str(e).endswith('.0') else str(e) for e in numeric_elements]

    sorted_elements = numeric_elements + string_elements

    return ",".join(sorted_elements)


def _pentafix(samps_dict, reverse=False):
    """Takes a dictionary of alleles and returns a dictionary with common Penta markers renamed for consistency."""
    if not reverse:
        if "Penta C" in samps_dict.keys():
            samps_dict["PentaC"] = samps_dict.pop("Penta C")
        elif "Penta_C" in samps_dict.keys():
            samps_dict["PentaC"] = samps_dict.pop("Penta_C")

        if "Penta D" in samps_dict.keys():
            samps_dict["PentaD"] = samps_dict.pop("Penta D")
        elif "Penta_D" in samps_dict.keys():
            samps_dict["PentaD"] = samps_dict.pop("Penta_D")

        if "Penta E" in samps_dict.keys():
            samps_dict["PentaE"] = samps_dict.pop("Penta E")
        elif "Penta_E" in samps_dict.keys():
            samps_dict["PentaE"] = samps_dict.pop("Penta_E")
    else:
        if "PentaC" in samps_dict.keys():
            samps_dict["Penta C"] = samps_dict.pop("PentaC")
        elif "Penta_C" in samps_dict.keys():
            samps_dict["Penta C"] = samps_dict.pop("Penta_C")

        if "PentaD" in samps_dict.keys():
            samps_dict["Penta D"] = samps_dict.pop("PentaD")
        elif "Penta_D" in samps_dict.keys():
            samps_dict["Penta D"] = samps_dict.pop("Penta_D")

        if "PentaE" in samps_dict.keys():
            samps_dict["Penta E"] = samps_dict.pop("PentaE")
        elif "Penta_E" in samps_dict.keys():
            samps_dict["Penta E"] = samps_dict.pop("Penta_E")

    return samps_dict


def _make_html(dataframe: pd.DataFrame):
    """Takes a dataframe and returns an interactive HTML table via dataTables."""

    table_html = dataframe.to_html(
        table_id="table1",
        index_names=False,
        index=False,
        border=0,
        classes=("display", "compact", "cell-border"),
    )

    html = f"""
    <html>
    <header>
        <link href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css" rel="stylesheet">
    </header>
    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            margin: 0px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        h1 {{
            text-align: center;
            background-color: #111111;
            color: white;
            padding: 10px 0px;
            width: 100%;
            margin: 0px;
            margin-bottom: 10px;
        }}
        .content {{
            flex:1;
        }}
        footer {{
            width: 100%;
            flex-shrink: 0;
            background: #111111;
            margin-top: 10px;
        }}
        ul {{
            padding: 1.25rem;
            text-align: center;
            color: #fff;
        }}
        ul li {{
            list-style-type: none;
            display: inline-block;
            margin: 0.25rem 0.75rem;
        }}
        ul a {{
            color: #fff;
            text-decoration: none;
        }}
        ul a:hover {{
            text-decoration: underline;
        }}
        table {{
            font-size: 8pt;
        }}
    </style>
    <body>
    <h1>STRprofiler Results</h1>
    <div style="width:95%; margin:auto;">
        {table_html}
    </div>
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js"
    integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready( function () {{
            $('#table1').DataTable({{
                // paging: false,
                // scrollY: 800,
            }});
        }});
    </script>
    </body>
    <footer>
        <ul>
            <li>
                Generated by STRprofiler (v{version("STRprofiler")}) on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </li>

            <li>
                <a href="https://pypi.org/project/strprofiler/"><i class="fa-brands fa-python"></i> PyPi</a>
            </li>

            <li>
                <a href="https://github.com/j-andrews7/strprofiler"><i class="fa-brands fa-github"></i> Github</a>
            </li>
        </ul>
    </footer>
    </html>
    """
    # return the html
    return html


def str_ingress(
    paths, sample_col="Sample", marker_col="Marker", sample_map=None, penta_fix=True
):
    """Reads in a list of paths and returns a pandas DataFrame of STR alleles in long format.

    :param paths: STR profile files to read in.
    :type paths: list of pathlib.Path
    :param sample_col: Name of sample column in each STR profile, defaults to "Sample"
    :type sample_col: str, optional
    :param marker_col: Name of marker identifier column in each STR profile,
        defaults to "Marker". Ignored if file in long format.
    :type marker_col: str, optional
    :param sample_map: Two column DataFrame containing sample identifiers in first column
        and new sample names to apply in second column, defaults to None
    :type sample_map: pandas.DataFrame, optional
    :param penta_fix: Whether to try to coerce "Penta" alleles to a common spelling, defaults to True
    :type penta_fix: bool, optional
    :return: A pandas DataFrame of STR alleles in long format.
    :rtype: pandas.DataFrame
    """

    samps_dicts = []

    for path in paths:
        path = Path(path)
        if path.suffix == ".xlsx":
            df = pd.read_excel(path)
        elif path.suffix == ".csv":
            df = pd.read_csv(path)
        elif path.suffix == ".tsv":
            df = pd.read_csv(path, sep="\t")
        elif path.suffix == ".txt":
            df = pd.read_csv(path, sep="\t")
        else:
            sys.exit("File extension: " + path.suffix + " in file: " + str(path) + " is not supported.")

        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        df.columns = df.columns.str.strip()

        # Collapse allele columns for each marker into a single column if in wide format.
        # ".0" strip handles edgecase where some alleles have a trailing ".0".
        if len(df.filter(like="Allele").columns) > 0:
            df["Alleles"] = (
                df.filter(like="Allele")
                .apply(
                    lambda x: ",".join(
                        [str(y).strip() for y in x if str(y) != "nan"]
                    ),
                    axis=1
                )
                .str.strip(",")
            )

            # Group and collect dict from each sample for markers and alleles.
            grouped = df.groupby(sample_col)

            for samp in grouped.groups.keys():
                samp_df = grouped.get_group(samp)
                samps_dict = samp_df.set_index(marker_col).to_dict()["Alleles"]
                samps_dict["Sample"] = samp

                # Remove duplicate alleles.
                for k in samps_dict.keys():
                    if k != "Sample":
                        samps_dict[k] = _clean_element(samps_dict[k])

                # Rename PentaD and PentaE from common spellings.
                if penta_fix:
                    samps_dict = _pentafix(samps_dict)

                samps_dicts.append(samps_dict)
        # If in long format, just collect dict from each sample for markers and alleles.
        else:
            df = df.replace(np.nan, "")
            df = df.astype(str)
            samps_list = df.to_dict("records")
            for s in samps_list:
                s["Sample"] = s.pop(sample_col)

                # Remove duplicate alleles, trim trailing ".0".
                for k in s.keys():
                    if k != "Sample":
                        s[k] = _clean_element(s[k])

                # Rename PentaD and PentaE from common spellings.
                if penta_fix:
                    s = _pentafix(s)

                samps_dicts.append(s)

    allele_df = pd.DataFrame(samps_dicts)

    # Replace sample names with sample map if provided.
    if sample_map is not None:
        for id in sample_map.iloc[:, 0]:
            allele_df.loc[allele_df["Sample"] == id, "Sample"] = sample_map.iloc[:, 1][
                sample_map.iloc[:, 0] == id
            ].to_string(header=False, index=False)

    # Set index to sample name.
    allele_df.set_index("Sample", inplace=True, verify_integrity=True)

    # Remove Nans.
    allele_df = allele_df.replace({np.nan: ""})

    return allele_df


def score_query(query, reference, use_amel=False, amel_col="AMEL"):
    """Calculates the Tanabe and Masters scores for a query sample against a reference sample.

    :param query: Alleles for query sample.
    :type query: dict
    :param reference: Alleles for reference sample.
    :type reference: dict
    :param use_amel: Whether to include amelogenin in scoring, defaults to False
    :type use_amel: bool, optional
    :param amel_col: Name of amelogenin column, defaults to "AMEL"
    :type amel_col: str, optional
    :return: Dictionary of scores for query sample against reference sample.
    :rtype: dict
    """

    n_r_alleles = 0
    n_q_alleles = 0

    n_shared_alleles = 0

    # Convert allele values to lists, removing markers with no alleles, and uniquifying alleles.
    query = {k: list(set(v.split(","))) for k, v in query.items() if v != ""}
    reference = {k: list(set(v.split(","))) for k, v in reference.items() if v != ""}

    # Get unique markers in query and reference.
    markers = list(set(query.keys()) & set(reference.keys()))

    # Remove amelogenin markers if use_amel is False.
    if use_amel is False:
        if amel_col in markers:
            markers.remove(amel_col)

    # Calculate the number of shared markers.
    n_shared_markers = len(markers)

    # Calculate the number of shared alleles.
    for m in markers:
        n_r_alleles += len(reference[m])
        n_q_alleles += len(query[m])
        n_shared_alleles += len(set(reference[m]) & set(query[m]))

    # Calculate the scores.
    tanabe_score = 100 * ((2 * n_shared_alleles) / (n_q_alleles + n_r_alleles))
    masters_q_score = 100 * (n_shared_alleles / n_q_alleles)
    masters_r_score = 100 * (n_shared_alleles / n_r_alleles)

    out = {
        "n_shared_markers": n_shared_markers,
        "query_sample": False,
        "n_shared_alleles": n_shared_alleles,
        "n_query_alleles": n_q_alleles,
        "n_reference_alleles": n_r_alleles,
        "tanabe_score": tanabe_score,
        "masters_query_score": masters_q_score,
        "masters_ref_score": masters_r_score,
    }

    return out


def mixing_check(alleles, three_allele_threshold=3):
    """Checks for potential sample mixing.

    :param alleles: Alleles for sample.
    :type alleles: dict
    :param three_allele_threshold: Number of markers with >2 alleles allowed before
        sample is flagged for potential mixing, defaults to 3
    :type three_allele_threshold: int, optional
    :return: Whether sample is potentially mixed.
    :rtype: bool
    """

    mixed = False
    past_th = 0

    for a in alleles.keys():
        all_a = alleles[a].split(",")
        if len(all_a) > 2:
            past_th += 1

    if past_th > three_allele_threshold:
        mixed = True

    return mixed


def make_summary(
    samp_df, alleles, tan_threshold, mas_q_threshold, mas_r_threshold, mixed, s_name
):
    """Generate summary line from full sample-specific output.

    :param samp_df: Sample-specific output DataFrame containing all comparisons to other samples.
    :type samp_df: pandas.DataFrame
    :param alleles: Alleles for sample.
    :type alleles: dict
    :param tan_threshold: Tanabe score threshold to report matching samples.
    :type tan_threshold: float
    :param mas_q_threshold: Masters (query) score threshold to report matching samples.
    :type mas_q_threshold: float
    :param mas_r_threshold: Masters (reference) score threshold to report matching samples.
    :type mas_r_threshold: float
    :param mixed: Flag for whether sample is potentially mixed.
    :type mixed: bool
    :param s_name: Sample name.
    :type s_name: str
    :return: Dictonary of summary line output for sample.
    :rtype: OrderedDict
    """

    tanabe_match = samp_df[samp_df["tanabe_score"] >= tan_threshold]
    tanabe_out = (
        tanabe_match["Sample"]
        + ": "
        + tanabe_match["tanabe_score"].round(decimals=2).astype(str)
    )
    tanabe_out = tanabe_out.tolist()
    tanabe_out = "; ".join(tanabe_out)

    # Get the top hits.
    top_hit = (
        samp_df["Sample"].iloc[1]
        + ": "
        + samp_df["tanabe_score"].round(decimals=2).astype(str).iloc[1]
    )
    next_hit = (
        samp_df["Sample"].iloc[2]
        + ": "
        + samp_df["tanabe_score"].round(decimals=2).astype(str).iloc[2]
    )

    masters_q_match = samp_df[samp_df["masters_query_score"] >= mas_q_threshold]
    masters_q_out = (
        masters_q_match["Sample"]
        + ": "
        + masters_q_match["masters_query_score"].round(decimals=2).astype(str)
    )
    masters_q_out = masters_q_out.tolist()
    masters_q_out = "; ".join(masters_q_out)

    masters_r_match = samp_df[samp_df["masters_ref_score"] >= mas_r_threshold]
    masters_r_out = (
        masters_r_match["Sample"]
        + ": "
        + masters_r_match["masters_ref_score"].round(decimals=2).astype(str)
    )
    masters_r_out = masters_r_out.tolist()
    masters_r_out = "; ".join(masters_r_out)

    summ_out = OrderedDict(
        {
            "Sample": s_name,
            "mixed": mixed,
            "top_hit": top_hit,
            "next_best": next_hit,
            "tanabe_matches": tanabe_out,
            "masters_query_matches": masters_q_out,
            "masters_ref_matches": masters_r_out,
        }
    )
    summ_out.update(alleles)

    return summ_out


def validate_api_markers(markers):
    """ Compare list of markers against controlled list of markers names from CLASTR.
    :param markers: List of markers to compare against controlled marker name list.
    :type markers: list
    :return: List of non-compliant marker names.
    :rtype: list
    """

    valid_api_markers = ["Amel",
                         "Amelogenin",
                         "CSF1PO",
                         "D2S1338",
                         "D3S1358",
                         "D5S818",
                         "D7S820",
                         "D8S1179",
                         "D13S317",
                         "D16S539",
                         "D18S51",
                         "D19S433",
                         "D21S11",
                         "FGA",
                         "Penta D",
                         "Penta E",
                         "PentaD",
                         "PentaE",
                         "TH01",
                         "TPOX",
                         "vWA",
                         "D1S1656",
                         "D2S441",
                         "D6S1043",
                         "D10S1248",
                         "D12S391",
                         "D22S1045",
                         "DXS101",
                         "DYS391",
                         "F13A01",
                         "F13B",
                         "FESFPS",
                         "LPL",
                         "Penta C",
                         "PentaC",
                         "SE33"]

    # remove extra fields, if present as keys may come from _clastr_query or other.
    query_markers = [marker for marker in markers if marker not in ["algorithm", "includeAmelogenin", "scoreFilter", "description"]]

    missing_markers = list(set(query_markers) - set(valid_api_markers))

    return missing_markers
