# Changelog

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