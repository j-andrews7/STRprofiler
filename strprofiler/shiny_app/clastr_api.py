import requests
import json
import pandas as pd
from flatten_json import flatten


def clastr_query(query, query_filter, include_amelogenin, score_filter):
    url = "https://www.cellosaurus.org/str-search/api/query/"

    if query_filter == "Tanabe":
        query['algorithm'] = 1
    elif query_filter == "Masters Query":
        query['algorithm'] = 2
    elif query_filter == "Masters Reference":
        query['algorithm'] = 3

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
    # The same logic from above applies, split the compount column name string,
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
    print(merged)
    # return final df

    # TO DO: Add query to top of merged DF before return.

    return merged


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
            "Penta D": "",
            "Penta E": "",
            "TH01": "7,9.3",
            "TPOX": "8",
            "vWA": "18",
            }

    # # stock from https://www.cellosaurus.org/str-search/help.html#5.1
    # data = {
    #         "Amelogenin": "X",
    #         "CSF1PO": "13,14",
    #         "D5S818": "13",
    #         "D7S820": "8",
    #         "D13S317": "12",
    #         "FGA": "24",
    #         "TH01": "8",
    #         "TPOX": "11",
    #         "vWA": "16",
    #         }

    r = clastr_query(data, 'Tanabe', False, 70)

    print(r)

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
