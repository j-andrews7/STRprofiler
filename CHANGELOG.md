# Changelog

## v0.5.1

**Release date: 09/23/2026**

Bug fixes:

 - The app's "Score Amelogenin" switch had no effect on "STRprofiler Database" and "Within File
   Query" batch searches, which always scored Amelogenin. They now honor the switch, as single
   queries already did.
 - `strprofiler compare --amel_col` was ignored, so an Amelogenin column not named `AMEL` was
   always scored, even without `--score_amel`. The option is now passed through to scoring.
 - A single reference with no scoreable alleles in common with a query no longer aborts an
   entire app batch query (or crashes a "Within File Query"); that reference is skipped instead.
 - Alleles typed into the app's marker boxes are now normalized the same way as database values
   (sorted, de-duplicated, with discarded calls removed), so the query row and mismatch
   highlighting agree with how the query is scored. A query made up only of discarded calls
   (e.g. `OL`) is now treated as empty.
 - App batch files containing the `Center`/`Passage` metadata columns are no longer rejected
   as having incompatible markers, and those columns are no longer sent to the CLASTR API.
 - The app's usage guide now documents the `Center`/`Passage` metadata columns.
 - **`-amel/--score_amel` is now a true flag for `strprofiler compare` and `strprofiler clastr`**,
   as the README already documented. It previously required a value (e.g. `-amel True`), and
   passing it bare consumed the next argument.

## v0.5.0

**Release date: 09/16/2026**

Bug fixes:

 - "Center" and "Passage" are no longer scored as STR markers. They were previously
   counted as shared markers and shared alleles by `score_query()`, which inflated
   similarity scores between samples that happened to share metadata (including for the
   example database bundled with the app). `score_query()` and `mixing_check()` now skip them via a
   new `metadata_cols` argument (defaulting to the `strprofiler.utils.METADATA_COLS`
   constant). **If you've used these metadata columns in a database in the past, this may affect your score.**
  - Similarly, `str_ingress()` no longer parses metadata columns as alleles, and takes a
   `metadata_cols` argument so custom non-marker columns can be declared.
 - CLASTR batch queries now send proper `algorithm: 3` for "Masters (vs. reference)". They
   previously erroneously sent `algorithm: 2`, which runs a Masters (vs. query) search.
 - Better "Penta" allele handling.
 - `_clean_element()` now drops empty allele tokens, so a trailing comma (e.g. `"12,"`) in
   a long-format input is no longer counted as an extra allele during scoring.
 - `make_summary()` no longer raises an `IndexError` when only the query row remains,
   which was reachable via `strprofiler compare -db` with a single-profile database whose
   sample name matched the query.
 - Corrected the `--mix_threshold` documentation, which described the threshold as counting
   markers with >= 2 alleles when the code counts markers with > 2 alleles. Also fixed
   `mix_threshold` and `sample_col` defaults in function signatures that disagreed with
   their `click` decorators.
 - Non-numeric allele calls are now discarded rather than counted. Off-ladder (`OL`),
   ambiguous (`?`), `NR`, `ND` and similar values were previously treated as ordinary
   alleles, so they inflated allele counts, could match each other between unrelated
   samples, and could push a diploid marker over the tri-allelic mixing threshold. The
   only non-numeric alleles retained are the Amelogenin sex markers, listed in the new
   `strprofiler.utils.NON_NUMERIC_ALLELES` constant. Filtering is applied in
   `str_ingress()`, `score_query()` and `mixing_check()`, so values typed directly into
   the app's marker boxes are covered too. A marker left with no valid alleles is treated
   as untyped and excluded from comparisons.
 - Allele values are better unified before comparison, so `"12.0"`, `" 12"` and `"12"`
   are recognized as the same allele, and `"x"` matches `"X"`.
 - `strprofiler --version` (and the `compare`, `clastr` and `app` subcommands) reported
   rich-click's version rather than STRprofiler's, which has now been corrected.
 - **`strprofiler clastr --scoring_mode` has moved from `-sm` to `-scm`.** `-sm` was
   declared twice, for both `--scoring_mode` and `--sample_map`, so click warned on every
   invocation and one option silently shadowed the other. `-sm` remains `--sample_map`, to
   match `strprofiler compare`. The `--sample_map` option was also missing from the
   `clastr` options table in the README.
 - Updated the GitHub Actions used by the test workflow, which was throwing a fit [#42](https://github.com/j-andrews7/STRprofiler/issues/42). `actions/cache` is
   now at v4, as the legacy cache service used by v1-v3 has been retired. 

Other changes:

 - **Support for Python 3.9 and 3.10 has been dropped.** The minimum supported version is
   now Python 3.11, as required by pandas 3.
 - Bumped `pandas` to `^3.0` and `numpy` to `^2.0`, and adapted to pandas 3 semantics
   (`DataFrame.set_index(verify_integrity=...)` is deprecated; duplicate sample
   identifiers now raise a `ValueError` directly).
 - CI now tests Python 3.11 through 3.14.

## v0.4.2

**Release date: 12/02/2024**

 - Add links to paper in app, README, etc.
 - Minor documentation fixes.

## v0.4.1

**Release date: 11/16/2024**

 - Improved error handling for edge cases and malformed inputs - [#36](https://github.com/j-andrews7/STRprofiler/issues/36), - [#35](https://github.com/j-andrews7/STRprofiler/issues/35)
 - Add docs and pypi links to app - [#38](https://github.com/j-andrews7/STRprofiler/issues/38)

## v0.4.0

**Release date: 09/30/2024**

 - Restructured app to use subcommands:
   - `strprofiler` is now `strprofiler compare`
   - `strprofiler-app` is now `strprofiler app`
   - `clastr` is now `strprofiler claster`
   - Parameters remain the same for each.
 - Tooltips added to inputs in Shiny application.
 - More graceful handling of edge cases that returned unhelpful feedback.
 - Better display of batch results in app that don't require download for viewing.

## v0.3.1

**Release date: 07/29/2024**

 - Catch no results and display a more helpful message - [#30](https://github.com/j-andrews7/STRprofiler/issues/30).

## v0.3.0

**Release date: 05/30/2024**

 - Added ability to query the CLASTR API for single or batch queries from within the STRprofiler 
 app - [#24](https://github.com/j-andrews7/strprofiler/pull/24).
 - Numerous UI tweaks for a more compact experience.

## v0.2.0

**Release date: 04/16/2024**

 - Addition of a new command, `strprofiler-app`, which launches an interactive Shiny
 application for single or batch queries of user-entered STR profiles against a user-provided database.
 This can be easily deployed to internal Shiny servers, Posit Connect, or shinyapps.io as an interface to a
 group's/lab's/consortium's STR profile database.

## v0.1.4

**Release date: 01/20/2024**

 - A new feature to allow one (or few) to many comparisons, as described in 
 [#11](https://github.com/j-andrews7/strprofiler/issues/11). Thanks to
 [MikeWLloyd](https://github.com/MikeWLloyd) for the contribution.

## v0.1.3

**Release date: 10/30/2023**

 - Additional bug fix for [#10](https://github.com/j-andrews7/strprofiler/issues/10), which
 was causing alleles ending in 0 to be truncated, e.g. 10 -> 1. 
 This was due to a parsing error when trailing ".0"s were being removed.

## v0.1.2

**Release date: 10/17/2023**

 - Bug fix for [#10](https://github.com/j-andrews7/strprofiler/issues/10), which
 was causing alleles ending in 0 to be truncated, e.g. 10 -> 1. 
 This was due to a parsing error when trailing ".0"s were being removed.

## v0.1.1

**Release date: 11/08/2022**

 - Multiple minor bug fixes, particularly with regard to making "penta" marker names consistent.
 - Add basic unit tests and test coverage, better organization/simplification of test data.
 - Add HTML summary output table.


## v0.1.0 - Initial Release

**Release date: 09/26/2022**

 - Provide CLI utility for STR profile comparisons and detection of sample mixing.