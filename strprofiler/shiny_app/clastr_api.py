import requests
import json
import pandas as pd
import numpy as np
from flatten_json import flatten
from strprofiler.utils import _pentafix, validate_api_markers


def _clastr_query(query, query_filter, include_amelogenin, score_filter):
    """
    :param query: dictionary in the format
        {"Amelogenin": "X,Y",
            "CSF1PO": "12",
            ... <additional markers>
        }
    Marker names have controlled vocab. Validated with strprofiler/utils:validate_api_markers
    :type query: dict
    :param query_filter: similiarity score to use. Options are: Tanabe, Masters Query, and Masters Reference
    :type query_filter: str
    :param includeAmelogenin: use Amelogenin for similarity scoring
    :type includeAmelogenin: bool
    :param score_filter: Minimum score to report as potential matches in summary table
    :type score_filter: int
    :return: pd.df with parsed json output or pd.df with error message.
    :rtype: pd.df
    """
    url = "https://www.cellosaurus.org/str-search/api/query/"

    dct = {k: [v] for k, v in query.items()}
    query_df = pd.DataFrame(dct)
    query_df["accession"] = "Query"

    if query_filter == "Tanabe":
        query["algorithm"] = 1
    elif query_filter == "Masters Query":
        query["algorithm"] = 2
    elif query_filter == "Masters Reference":
        query["algorithm"] = 3

    query = _pentafix(query, reverse=True)

    query["includeAmelogenin"] = include_amelogenin
    query["scoreFilter"] = score_filter

    r = requests.post(url, data=json.dumps(query))

    # JSON response:
    #   'description': '',
    #   'cellosaurusRelease': '48.0',
    #   'runOn': '2024-Apr-25 12:45:40 UTC+0',
    #   'toolVersion': '1.4.4',
    #   'searchSpace': 8581,
    #   'parameters': {...
    #   'results': [{ ...
    # FULL STRUCTURE OUTLINED BELOW.

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return pd.DataFrame({"Error": [str(e)]})

    df = pd.DataFrame.from_dict(r.json()["results"])

    if df.empty:
        return pd.DataFrame({"No CLASTR Result": []})

    flattened = [flatten(d) for d in r.json()["results"]]
    df = pd.DataFrame(flattened)

    # profiles[0] has "bestScore" returns, but a second return is possible.
    # per CLASTR there will be at most 2 returns per profile.
    # Markers within profiles are split into individual "value":allele pairs.
    # First select alleles, and then concat alleles by return and marker
    markers = df.filter(regex="^profiles_*_.*_value").T
    markers[["A", "profileID", "C", "markerID", "E", "F", "G"]] = markers.index.str.split("_", n=7, expand=False).tolist()
    markers.drop(["A", "C", "E", "F", "G"], axis=1, inplace=True)
    # Melt dataframe to: [profileID, markerID, resultID, allele] for cat on profileID/markerID/resultID
    melted_markers = pd.melt(markers, id_vars=["profileID", "markerID"], var_name="resultID", value_name="allele")

    # each profile has its own score as well. these also need to be tracked to trace "best" and "worst" in multi-return cases.
    scores = df.filter(regex="^profiles_*_.*_score").T
    scores[["A", "profileID", "C"]] = scores.index.str.split("_", n=3, expand=False).tolist()
    scores.drop(["A", "C"], axis=1, inplace=True)
    melted_scores = pd.melt(scores, id_vars=["profileID"], var_name="resultID", value_name="score").dropna()

    # Join resultID and markerID index to grouped joined allele strings.
    allele_cat_markers = pd.concat([
        melted_markers[["resultID", "profileID", "markerID"]],
        melted_markers.groupby(["resultID", "profileID", "markerID"], as_index=True)
        .transform(lambda x: ",".join(map(str, x)).replace(",nan", "").replace("nan", ""))
    ], axis=1).drop_duplicates(subset=["resultID", "profileID", "markerID"])

    pd.merge(allele_cat_markers, melted_scores,  how="inner", on=["profileID", "resultID"])

    # Marker names are not consistant across results. MarkerName[1] != MarkerName[1] in all returns.
    # We must track marker name by profile, index, and result.
    # The same logic from above applies, split the compound column name string,
    # Melt on profileID and markerID, and then merge with concat allele made above.
    # Finally, pivot into a table and rejoin to higher level results.
    marker_names = df.filter(regex="^profiles_*_.*_name").T
    marker_names[["A", "profileID", "C", "markerID", "E"]] = marker_names.index.str.split("_", n=5, expand=False).tolist()
    marker_names.drop(["A", "C", "E"], axis=1, inplace=True)

    melted_markers = pd.melt(marker_names, id_vars=["profileID", "markerID"],
                             var_name="resultID", value_name="markerName").dropna().drop_duplicates(subset=["profileID", "markerID", "resultID"])

    markers_names_alleles = pd.merge(allele_cat_markers, melted_markers,  how="inner", on=["profileID", "markerID", "resultID"])

    pivot_markers_names_alleles = markers_names_alleles.pivot(index=["profileID", "resultID"], columns="markerName", values="allele")

    try:
        merged = pd.merge(df[["accession", "name", "species", "bestScore", "problem"]],
                          pivot_markers_names_alleles, left_index=True, right_on="resultID")
    except KeyError:
        merged = pd.merge(df[["accession", "name", "species", "bestScore"]], pivot_markers_names_alleles, left_index=True, right_on="resultID")

    merged["accession_link"] = "https://web.expasy.org/cellosaurus/" + merged["accession"]

    merged = _pentafix(merged)

    merged_scored = pd.merge(merged, melted_scores, left_on=["profileID", "resultID"], right_on=["profileID", "resultID"])

    # For returns with 2 profiles, annotate which of the pair is best / worst.
    # group by accession, and mutate a new accession column when multi_return and profile score == bestScore (best)
    # when multi_return and profile score != bestScore (worst), and all other cases (single returns)
    merged_scored["multi_group"] = merged_scored.groupby("accession")["accession"].transform("size") > 1
    merged_scored["new"] = np.where(merged_scored["multi_group"] & (merged_scored["bestScore"] == merged_scored["score"]),
                                    merged_scored["accession"] + " (Best)",
                                    np.where(merged_scored["bestScore"] != merged_scored["score"],
                                             merged_scored["accession"] + " (Worst)",
                                             merged_scored["accession"]))
    merged_scored["accession"] = merged_scored["new"]

    # # add the query line to the top of merged_scored, and reorder columns
    query_added = pd.concat([query_df, merged_scored.drop(["new", "bestScore", "multi_group"], axis=1)]).reset_index(drop=True)

    query_added["score"] = query_added["score"].map("{0:.2f}".format).replace("nan", "")

    if "problem" in query_added.columns:
        query_added = query_added[["accession", "name", "species", "score", "accession_link", "problem"] +
                                  [c for c in query_added if c not in
                                   ["accession", "name", "species", "score", "accession_link", "problem"]]].fillna("")
    else:
        query_added = query_added[["accession", "name", "species", "score", "accession_link"] +
                                  [c for c in query_added if c not in ["accession", "name", "species", "score", "accession_link"]]].fillna("")

    return query_added


def _clastr_batch_query(query, query_filter, include_amelogenin, score_filter):
    """
    :param query: list of dictionaries in the format
        [{
            "description": "Example 1",
            "Amelogenin": "X",
            ... <additional markers>
            }, {
            "description": "Example 2",
            "Amelogenin": "X, Y",
            ... <additional markers>
        }]
    'description' is a required key.
    Marker names have controlled vocab. Validated with strprofiler/utils:validate_api_markers
    :type query: list
    :param query_filter: similiarity score to use. Options are: Tanabe, Masters Query, and Masters Reference
    :type query_filter: str
    :param includeAmelogenin: use Amelogenin for similarity scoring
    :type includeAmelogenin: bool
    :param score_filter: Minimum score to report as potential matches in summary table
    :type score_filter: int
    :return: valid post request return, or pd.df with error message.
    Valid post request contains bytes in xlsx format accessed via (r.iter_content(chunk_size=128))
    :rtype: request result or pd.df
    """
    url = "https://www.cellosaurus.org/str-search/api/batch/"

    query = [_pentafix(item, reverse=True) for item in query]

    if query_filter == "Tanabe":
        query = [dict(item, **{"algorithm": 1}) for item in query]
    elif query_filter == "Masters Query":
        query = [dict(item, **{"algorithm": 2}) for item in query]
    elif query_filter == "Masters Reference":
        query = [dict(item, **{"algorithm": 2}) for item in query]

    query = [dict(item, **{"includeAmelogenin": include_amelogenin}) for item in query]
    query = [dict(item, **{"scoreFilter": score_filter}) for item in query]
    query = [dict(item, **{"outputFormat": "xlsx"}) for item in query]

    r = requests.post(url, data=json.dumps(query))

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return pd.DataFrame({"Error": [str(e)]})

    return r


if __name__ == "__main__":
    # url = "https://www.cellosaurus.org/str-search/api/query/%"
    # Use above URL for 400 error

    # sample J000077451
    # data = {"Amelogenin": "X,Y",
    #         "CSF1PO": "12",
    #         "D2S1338": "17,19",
    #         "D3S1358": "15",
    #         "D5S818": "11,12",
    #         "D7S820": "11,12",
    #         "D8S1179": "12,15",
    #         "D13S317": "8",
    #         "D16S539": "13",
    #         "D18S51": "14",
    #         "D19S433": "14",
    #         "D21S11": "31,31.2",
    #         "FGA": "23",
    #         "PentaD": "",
    #         "PentaE": "",
    #         "TH01": "7,9.3",
    #         "TPOX": "8",
    #         "vWA": "18",
    #         "NoGoodVeryBad": "I'm not a valid marker. However, that is ok. We catch this now."
    #         }

    # stock from https://www.cellosaurus.org/str-search/help.html#5.1
    # data = {
    #         "Amelogenin": "X",
    #         "CSF1PO": "13,14",
    #         "D5S818": "13",
    #         "D7S820": "8,9",
    #         "D13S317": "12",
    #         "FGA": "24",
    #         "TH01": "8",
    #         "TPOX": "11",
    #         "vWA": "16"
    #         }

    # # stock example from https://www.cellosaurus.org/str-search/. Includes profile[0] and profile[1]
    data = {"Amelogenin": "X",
            "CSF1PO": "11,12",
            "D2S1338": "19,23",
            "D3S1358": "15,17",
            "D5S818": "11,12",
            "D7S820": "10",
            "D8S1179": "10",
            "D13S317": "11,12",
            "D16S539": "11,12",
            "D18S51": "13",
            "D19S433": "14",
            "D21S11": "29,30",
            "FGA": "20,22",
            "PentaD": "11,13",
            "PentaE": "14,16",
            "TH01": "6,9",
            "TPOX": "8,9",
            "vWA": "17,19"
            }

    malformed_markers = validate_api_markers(data.keys())

    print(malformed_markers)

    r = _clastr_query(data, "Tanabe", False, 80)

    print(r)

    batch_data = [{
        "description": "Example 1",
        "Amelogenin": "X",
        "CSF1PO": "13,14",
        "D5S818": "13",
        "D7S820": "8",
        "D13S317": "12",
        "FGA": "24",
        "TH01": "8",
        "TPOX": "11",
        "vWA": "16",
        }, {
        "description": "Example 2",
        "Amelogenin": "X, Y",
        "CSF1PO": "13",
        "D5S818": "13, 14",
        "D7S820": "8, 19",
        "D13S317": "11, 12",
        "FGA": "24",
        "TH01": "8",
        "TPOX": "11",
        "vWA": "15",
        "outputFormat": "xlsx"
        }]

    r = _clastr_batch_query(batch_data, "Tanabe", False, 70)

    with open("testing.xlsx", "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)


#  JSON data structure:
# {
#     "description": "",
#     "cellosaurusRelease": "48.0",
#     "runOn": "2024-Apr-30 18:15:31 UTC+0",
#     "toolVersion": "1.4.4",
#     "searchSpace": 8581,
#     "parameters": {
#         "species": "Homo sapiens (Human)",
#         "algorithm": "Tanabe",
#         "scoringMode": "Non-empty makers",
#         "scoreFilter": 70,
#         "minMarkers": 8,
#         "maxResults": 200,
#         "includeAmelogenin": false,
#         "markers": [ {
#                 "name": "Amelogenin",
#                 "alleles": [
#                     {
#                         "value": "X"
#                     },
#                     {
#                         "value": "Y"
#                     }
#                 ]
#             }, ... ]
#     },
#     "results": [
#             {
#                 "accession": "CVCL_2335",
#                 "name": "CCD-1076Sk",
#                 "species": "Homo sapiens (Human)",
#                 "bestScore": 72.0,
#                 "problematic": false,
#                 "profiles": [
#                     {
#                         "score": 72.0,
#                         "markerNumber": 8,
#                         "alleleNumber": 14,
#                         "markers": [
#                             {
#                                 "name": "Amelogenin",
#                                 "conflicted": false,
#                                 "searched": true,
#                                 "sources": [],
#                                 "alleles": [
#                                     {
#                                         "value": "X",
#                                         "matched": true
#                                     },
#                                     {
#                                         "value": "Y",
#                                         "matched": true
#                                     }
#                                 ]
#                             },
#                             ...
#                     }
#                     <Note: 2 profiles possible per result>
#                     <best score result is profile[0]>
#             }
#             <result 2 ... n >
#     ]
