import strprofiler.utils as sp
import pandas as pd
from math import nan
from collections import OrderedDict
import time


def _single_query(
    query,
    str_database,
    use_amel,
    three_allele_threshold,
    query_filter,
    query_filter_threshold,
):

    if query_filter == "Tanabe":
        query_filter_name = "tanabe_score"
        drop_cols = [
            "masters_query_score",
            "masters_ref_score",
            "query_sample",
            "n_query_alleles",
            "n_reference_alleles",
        ]
    elif query_filter == "Masters Query":
        query_filter_name = "masters_query_score"
        drop_cols = [
            "tanabe_score",
            "masters_ref_score",
            "query_sample",
            "n_query_alleles",
            "n_reference_alleles",
        ]
    elif query_filter == "Masters Reference":
        query_filter_name = "masters_ref_score"
        drop_cols = [
            "tanabe_score",
            "masters_query_score",
            "query_sample",
            "n_query_alleles",
            "n_reference_alleles",
        ]

    current_time = time.strftime("%H:%M", time.localtime())

    mixed = sp.mixing_check(
        alleles=query, three_allele_threshold=three_allele_threshold
    )

    q_out = {
        "Sample": "Query",
        "mixed": mixed,
        "query_sample": True,
        "n_shared_markers": nan,
        "n_shared_alleles": nan,
        "n_query_alleles": nan,
        "n_reference_alleles": nan,
        "tanabe_score": nan,
        "masters_query_score": nan,
        "masters_ref_score": nan,
        "Center": nan,
        "Passage": nan
    }
    q_out.update(query)

    # Put query sample first.
    samp_comps = [q_out]

    for sa in str_database.keys():
        r = str_database[sa]

        # catch cases where ref is empty or otherwise invalid.
        try:
            scores = sp.score_query(
                query=query, reference=r, use_amel=use_amel, amel_col="Amelogenin"
            )
        except ZeroDivisionError:
            pass

        # Create dict of scores for each sample comparison.
        samp_out = OrderedDict({"Sample": sa})
        samp_out.update(scores)
        samp_out.update(r)

        samp_comps.append(samp_out)

    # Create DataFrame of scores for each sample comparison.
    full_samp_out = pd.DataFrame(samp_comps)
    full_samp_out.sort_values(
        by=query_filter_name, ascending=False, inplace=True, na_position="first"
    )

    full_samp_out = full_samp_out.round(
        {"tanabe_score": 2, "masters_query_score": 2, "masters_ref_score": 2}
    )

    full_samp_out = full_samp_out[
        (full_samp_out[query_filter_name] >= query_filter_threshold)
        | (full_samp_out.index == 0)
    ]

    full_samp_out.drop(columns=drop_cols, inplace=True)

    full_samp_out.rename(
        columns={
            "mixed": "Mixed Sample",
            "n_shared_markers": "Shared Markers",
            "n_shared_alleles": "Shared Alleles",
            "tanabe_score": "Tanabe Score",
            "masters_query_score": "Masters Query Score",
            "masters_ref_score": "Masters Ref Score",
        },
        inplace=True,
    )

    return full_samp_out


def _batch_query(
    query_df,
    str_database,
    use_amel,
    three_allele_threshold,
    tan_threshold,
    mas_q_threshold,
    mas_r_threshold,
):

    summaries = []

    for s in query_df.keys():
        q = query_df[s]
        # Check for sample mixing.
        mixed = sp.mixing_check(
            alleles=q, three_allele_threshold=three_allele_threshold
        )

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

        for sa in str_database.keys():
            r = str_database[sa]

            try:
                scores = sp.score_query(query=q, reference=r, use_amel=use_amel)
            except ZeroDivisionError:
                pass
            except Exception:
                return False

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

        # Generate summary of scores for given sample.
        summ = sp.make_summary(
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

    summaries_out = summaries[
        [
            "Sample",
            "mixed",
            "top_hit",
            "next_best",
            "tanabe_matches",
            "masters_query_matches",
            "masters_ref_matches",
        ]
    ]

    summaries_ret = summaries_out.rename(
        columns={
            "mixed": "Mixed Sample",
            "top_hit": "Top Match",
            "next_best": "Next Best Match",
            "tanabe_matches": "Tanabe Matches",
            "masters_query_matches": "Masters Query Matches",
            "masters_ref_matches": "Masters Ref Matches",
        }
    )

    return summaries_ret


def _file_query(
    query_df,
    use_amel,
    three_allele_threshold,
    tan_threshold,
    mas_q_threshold,
    mas_r_threshold,
):

    summaries = []

    for s in query_df.keys():
        q = query_df[s]
        # Check for sample mixing.
        mixed = sp.mixing_check(
            alleles=q, three_allele_threshold=three_allele_threshold
        )

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

        for sa in query_df.keys():
            if sa != s:
                r = query_df[sa]
                scores = sp.score_query(query=q, reference=r, use_amel=use_amel)

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

        # Generate summary of scores for given sample.
        summ = sp.make_summary(
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

    summaries_out = summaries[
        [
            "Sample",
            "mixed",
            "top_hit",
            "next_best",
            "tanabe_matches",
            "masters_query_matches",
            "masters_ref_matches",
        ]
    ]

    summaries_ret = summaries_out.rename(
        columns={
            "mixed": "Mixed Sample",
            "top_hit": "Top Match",
            "next_best": "Next Best Match",
            "tanabe_matches": "Tanabe Matches",
            "masters_query_matches": "Masters Query Matches",
            "masters_ref_matches": "Masters Ref Matches",
        }
    )

    return summaries_ret
