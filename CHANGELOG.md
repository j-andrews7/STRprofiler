# Changelog

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