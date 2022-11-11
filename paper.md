---
title: 'strprofiler: A Python package and CLI tool for short tandem repeat profile comparisons'
tags:
  - python
  - cli
  - str profiling
  - short tandem repeats
  - model comparison
  - cell line fidelity
  - cell line authentication
  - sample mixing
authors:
  - name: Jared M. Andrews
    orcid: 0000-0002-0780-6248
    equal-contrib: false
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Suzanne J. Baker
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
affiliations:
 - name: Department of Developmental Neurobiology, St. Jude Children's Research Hospital, USA
   index: 1
date: 8 November 2022
bibliography: paper.bib
---

# Summary

Human cell lines have been utilized extensively for biological and pharmaceutical research, but they are at risk for cross-contamination and genetic drift over time.
Cell line misidentification can lead to erroneous conclusions and wasted resources [@atcc; @tanabe; @capes-davis], so ensuring the authenticity of cell lines is critical for the integrity of scientific research.
Short tandem repeat (STR) profiling is the recommended method for cell line authentication, which requres the comparison of STR profiles between a cell line and a reference sample.
Generation of cell lines from primary tissue is expensive and time-consuming, so it is best practice for groups that generate them to serially profile them to ensure their authenticity over time.

# Statement of need

`strprofiler` is a Python package for comparisons of short tandem repeat (STR) profiles. 
Profiles are frequently generated after cell line generation and throughout maintenance to authenticate their identify, identify sample mixing, and measure genetic drift during culture. 
`strprofiler` provides a simple command line interface (CLI) for comparing STR profiles and detecting sample mixing, which can prove a time-consuming and tedious task when performed manually.
While there exist comprehensive STR profile databases and tools, such as the [Cellusaurus STR Similarity Search Tool (CLASTR)](https://www.cellosaurus.org/str-search/) [@CLASTR], that allow comparisons to established cell lines in a low-throughput manner, these databases and tools are inadequate for research groups that generate, utilize, and maintain their own models not available through public repositories. 
`strprofiler` allows researchers to quickly and easily compare all of their STR profiles to each other.

# Usage

`strprofiler` was designed to be simple to use and interpret. 
It offers a rich CLI that takes flexible STR profile formats as input. 
For all input STR profiles, each profile will be compared to every other profile provided and scored for similarity using the Tanabe [@tanabe], Masters (vs. query), and Masters (vs. reference) [@masters] algorithms. 
All three have proven robust for assessing sample similarity, and an 80% similarity threshold discriminates unrelated cell lines effectively [@capes-davisMatchCriteria]. 
By default, this is the threshold `strprofiler` uses for all algorithms to count a profile as a match. 
In instances where samples have been previously documented as having highly variable STR profiles or known microsatellite instability, it may be appropriate for these thresholds to be lowered.

`strprofiler` returns two types of output files. 
The first is a summary file containing a record for each STR profile, its top matches with the Tanabe algorithm, all matches for each algorithm that meet the scoring threshold, and a flag for potential sample mixing based on the number of markers with 3 or more alleles detected.
The second is a profile-specific file with that profile queried against all others. 
This file allows for closer interrogation of samples with potential mixing.

Full descriptions of input/output formats and additional parameters are available at [ReadTheDocs](https://strprofiler.readthedocs.io/en/latest/). `strprofiler` is available on [PyPI](https://pypi.org/project/strprofiler/).

# Similarity Scoring Algorithms

`strprofiler` utilizes three similarity scoring algorithms for comparing STR profiles:

 - Tanabe, also known as the Sørenson-Dice coefficient [@tanabe]:

$$ score = \frac{2 * no.shared.alleles}{no.query.alleles + no.reference.alleles} $$

 - Masters (vs. query) [@masters]: 

$$ score = \frac{no.shared.alleles}{no.query.alleles} $$

 - Masters (vs. reference) [@masters]: 

$$ score = \frac{no.shared.alleles}{no.reference.alleles} $$

The Masters algorithms are particularly useful for determining the potential contaminating samples when unintentional mixing occurs.


# Acknowledgements

We would like to acknowledge Lawryn Kasper for helpful feedback and testing of this project. We acknowledge support from the National Cancer Insitute (NCI) of the National Institutes of Health under award number P01CA096832.

# References