import requests
import json
import pandas as pd
from flatten_json import flatten
from strprofiler.utils import _pentafix, validate_api_markers


def _clastr_query(query, query_filter, include_amelogenin, score_filter):
    url = "https://www.cellosaurus.org/str-search/api/query/"

    dct = {k: [v] for k, v in query.items()}
    query_df = pd.DataFrame(dct)
    query_df['accession'] = 'Query'

    if query_filter == "Tanabe":
        query['algorithm'] = 1
    elif query_filter == "Masters Query":
        query['algorithm'] = 2
    elif query_filter == "Masters Reference":
        query['algorithm'] = 3

    query = _pentafix(query, reverse=True)

    query['includeAmelogenin'] = include_amelogenin
    query['scoreFilter'] = score_filter

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

    df = pd.DataFrame.from_dict(r.json()['results'])

    if df.empty:
        return pd.DataFrame({"No Clastr Result": []})

    flattened = [flatten(d) for d in r.json()['results']]
    df = pd.DataFrame(flattened)

    # profiles[0] has 'bestScore' returns.
    # Markers within profiles[0] are split by each allele 'value'
    # First select alles, and then concat alleles by return and marker
    markers = df.filter(regex='^profiles_0_.*_value').T
    markers[['A', 'B', 'C', 'markerID', 'E', 'F', 'G']] = markers.index.str.split('_', n=7, expand=False).tolist()
    markers.drop(['A', 'B', 'C', 'E', 'F', 'G'], axis=1, inplace=True)

    # Melt dataframe to: [markerID, resultID, allele] for cat on markerID/resultID
    melted_markers = pd.melt(markers, id_vars=['markerID'], var_name='resultID', value_name='allele')

    # Join resultID and markerID index to grouped joined allele strings.
    allele_cat_markers = pd.concat([
        melted_markers[['resultID', 'markerID']],
        melted_markers.groupby(['resultID', 'markerID'], as_index=True).transform(lambda x: ','
                                                                                  .join(map(str, x)).replace(",nan", "").replace("nan", ""))
    ], axis=1).drop_duplicates(subset=['resultID', 'markerID'])

    # Marker names are not consistant across results. MarkerName[1] != the same thing in all cases.
    # We must track marker name by index by result.
    # The same logic from above applies, split the compound column name string,
    # Melt on markerID, and then merge with concat allele made above.
    # Finally, pivot into a table and rejoin to higher level results.
    marker_names = df.filter(regex='^profiles_0_.*_name').T
    marker_names[['A', 'B', 'C', 'markerID', 'E']] = marker_names.index.str.split('_', n=5, expand=False).tolist()
    marker_names.drop(['A', 'B', 'C', 'E'], axis=1, inplace=True)

    melted_markers = pd.melt(marker_names, id_vars=['markerID'],
                             var_name='resultID', value_name='markerName').dropna().drop_duplicates(subset=['markerID', 'resultID'])

    markers_names_alleles = pd.merge(allele_cat_markers, melted_markers,  how='inner', on=['markerID', 'resultID'])

    pivot_markers_names_alleles = markers_names_alleles.pivot(index=['resultID'], columns='markerName', values='allele')

    try:
        merged = pd.merge(df[['accession', 'name', 'species', 'bestScore', 'problem']],
                          pivot_markers_names_alleles, left_index=True, right_on='resultID')
    except KeyError:
        merged = pd.merge(df[['accession', 'name', 'species', 'bestScore']], pivot_markers_names_alleles, left_index=True, right_on='resultID')

    merged['accession_link'] = "https://web.expasy.org/cellosaurus/" + merged['accession']

    merged = _pentafix(merged)

    # add the query line to the top of merged, and reorder columns

    query_added = pd.concat([query_df, merged]).reset_index(drop=True)
    query_added["bestScore"] = query_added['bestScore'].map("{0:.2f}".format).replace("nan", "")

    if 'problem' in query_added.columns:
        query_added = query_added[['accession', 'name', 'species', 'bestScore', 'accession_link', 'problem'] +
                                  [c for c in query_added if c not in
                                   ['accession', 'name', 'species', 'bestScore', 'accession_link', 'problem']]].fillna('')
    else:
        query_added = query_added[['accession', 'name', 'species', 'bestScore', 'accession_link'] +
                                  [c for c in query_added if c not in ['accession', 'name', 'species', 'bestScore', 'accession_link']]].fillna('')

    return query_added


def _clastr_batch_query(query, query_filter, include_amelogenin, score_filter):
    url = "https://www.cellosaurus.org/str-search/api/batch/"

    query = [_pentafix(item, reverse=True) for item in query]

    if query_filter == "Tanabe":
        query = [dict(item, **{'algorithm': 1}) for item in query]
    elif query_filter == "Masters Query":
        query = [dict(item, **{'algorithm': 2}) for item in query]
    elif query_filter == "Masters Reference":
        query = [dict(item, **{'algorithm': 2}) for item in query]

    query = [dict(item, **{'includeAmelogenin': include_amelogenin}) for item in query]
    query = [dict(item, **{'scoreFilter': score_filter}) for item in query]
    query = [dict(item, **{'outputFormat': 'xlsx'}) for item in query]

    r = requests.post(url, data=json.dumps(query))

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return pd.DataFrame({"Error": [str(e)]})

    return r


if __name__ == '__main__':
    # url = "https://www.cellosaurus.org/str-search/api/query/%"
    # Use above URL for 400 error

    # sample J000077451
    data = {"Amelogenin": "X,Y",
            "CSF1PO": "12",
            "D2S1338": "17,19",
            "D3S1358": "15",
            "D5S818": "11,12",
            "D7S820": "11,12",
            "D8S1179": "12,15",
            "D13S317": "8",
            "D16S539": "13",
            "D18S51": "14",
            "D19S433": "14",
            "D21S11": "31,31.2",
            "FGA": "23",
            "PentaD": "",
            "PentaE": "",
            "TH01": "7,9.3",
            "TPOX": "8",
            "vWA": "18",
            "NoGoodVeryBad": "I'm not a valid marker. However, that is ok. We catch this now."
            }

    # # stock from https://www.cellosaurus.org/str-search/help.html#5.1
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

    # # stock example from https://www.cellosaurus.org/str-search/
    # data = {"Amelogenin": "X",
    #         "CSF1PO": "11,12",
    #         "D2S1338": "19,23",
    #         "D3S1358": "15,17",
    #         "D5S818": "11,12",
    #         "D7S820": "10",
    #         "D8S1179": "10",
    #         "D13S317": "11,12",
    #         "D16S539": "11,12",
    #         "D18S51": "13",
    #         "D19S433": "14",
    #         "D21S11": "29,30",
    #         "FGA": "20,22",
    #         "PentaD": "11,14",
    #         "PentaE": "14,16",
    #         "TH01": "6,9",
    #         "TPOX": "8,9",
    #         "vWA": "17,19"
    #         }

    malformed_markers = validate_api_markers(data.keys())

    print(malformed_markers)

    r = _clastr_query(data, 'Tanabe', False, 70)

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

    r = _clastr_batch_query(batch_data, 'Tanabe', False, 70)

    with open('testing.xlsx', 'wb') as fd:
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
#                     <Note: more than 1 profile possible per result>
#                     <best score result is profile[0]>
#             }
#             <result 2 ... n >
#     ]
