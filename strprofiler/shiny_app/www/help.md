---
title: "STRprofiler Shiny Application Usage"
author:
  - "Michael W. Lloyd, The Jackson Laboratory"
  - "Jared Andrews, St. Jude Children's Research Hospital"
output: 
  html_document:
    theme: spacelab
    toc: true
    toc_float: true
    toc_depth: 4
    number_sections: false
    self_contained: true
---

**This site and tool are intended for research purposes only.**

# Database Queries  
For a provided sample entered manually in the `Database Single Query` or sample(s) uploaded from a batch file in the `Database Batch Query` tab, 
`STRprofiler` will generate a report that includes the similarity scores (described below) as computed against a database of known STR profiles.  

The report will differ depending on if an individual sample or batch of samples is provided.   

## Default Database

Current data underlying the default database were provided by [The Jackson Laboratory PDX program](https://tumor.informatics.jax.org/mtbwi/pdxSearch.do), and the [NCI Patient-Derived Models Repository (PDMR)](https://pdmr.cancer.gov/).

If this app is hosted with a custom database, please contact the host for information on the database source.  

## CLASTR / Cellosaurus API Query

Query of the [Cellosaurus](https://www.cellosaurus.org/description.html) (Bairoch, 2018) cell line database is also available for single and batch samples via the [CLASTR](https://www.cellosaurus.org/str-search/) (Robin, Capes-Davis, and Bairoch, 2019) [REST API](https://www.cellosaurus.org/str-search/help.html#5).  

---

## Single Query Report

For individual samples, a report is generated with the following fields when 'STRprofiler Database' is selected as the search type.  

| Output Field | Description |
| :--- |    :----   |
| Mixed Sample      | Flag to indicate sample mixing. Sample mixing is determined by the "'Mixed' Sample Threshold" option. If more markers are tri+ allelic than the threshold, samples are flagged as potentially mixed. |
| Shared Markers   | Number of markers shared between the query and database sample. |
| Shared Alleles   | Number of alleles shared between the query and database sample. |
| Tanabe Score | Tanabe similarity score between the query and database sample (if Tanabe selected). |
| Master Query Score | Master 'Query' similarity score between the query and database sample (if Master Query selected). |
| Master Ref Score | Master 'Reference' similarity score between the query and database sample (if Master Ref selected). |
| Markers 1 ... n | Marker alleles with mismatches highlighted. |

The report is filtered to include only those samples with greater than or equal to the `Similarity Score Filter Threshold` defined by the user, and report only the similarity score selected.    

When `Cellosaurus Database (CLASTR)` is selected as the search type, a report is generated with the following fields:  

| Output Field | Description |
| :--- |    :----   |
| Accession      | Cellosaurus cell line accession ID. Links are provided to each accession information page. |
| Name   | Cell line name. |
| Score | Similarity score between the query and cell line sample. Reported score reflectes the selected Similarity Score Filter. |
| Markers 1 ... n | Marker alleles with mismatches highlighted. |

The report is filtered to include only those samples with greater than or equal to the `Similarity Score Filter Threshold` defined by the user.  

---

## Batch Query Report 

For batched samples, a summary report is generated. 

| Output Field | Description |
| :---        |    :----   |
| Mixed Sample | Flag to indicate sample mixing. Sample mixing is determined by the "'Mixed' Sample Threshold" option. If more markers have more than 3 alleles for this number of markers, the sample will be flagged as potentially mixed. |
| Top Match |	Name and Tanabe score of top match to sample. |
| Next Best Match |	Name and Tanabe score of next best match to sample. |
| Tanabe Matches | Name and Tanabe score of matches above scoring threshold to sample. |
| Master Query Matches | Name and Masters (vs. query) score of matches above scoring threshold to sample. |
| Master Ref Matches | Name and Masters (vs. reference) score of matches above scoring threshold to sample. |

The report is filtered to include only those samples with greater than or equal to the `Similarity Score Filter Thresholds` defined by the user.  

When `Cellosaurus Database (CLASTR)` is selected as the search type, a report is generated in XLSX format, and can be downloaded via the `Download XLSX` button. These results will not be displayed in the app window directly, they must be downloaded.


## Database File Management

Users can upload custom database files. The files must be in CSV format. A 'Sample' header must be present, but custom marker names may be used. Note that to score `Amelogenin` using the option provided, there must be a `Amelogenin` header in the uploaded file.  

---

# Reported Similarity Scores

1. <a href="https://www.doi.org/10.11418/jtca1981.18.4_329" target="_blank">Tanabe, AKA the Sørenson-Dice coefficient</a>:  

<p align="center">
  <img src="tanabe.png"/>
</p>

2. <a href="https://www.ncbi.nlm.nih.gov/pubmed/11416159" target="_blank">Masters (vs. query)</a>:  

<p align="center">
  <img src="masters_query.png"/>
</p>

3. <a href="https://www.ncbi.nlm.nih.gov/pubmed/11416159" target="_blank">Masters (vs. reference)</a>:  


<p align="center">
  <img src="masters_ref.png"/>
</p>

---

# Query Options

## Sample Query Options

* Amelogenin scoring is excluded by default but can be included by selecting the option.  
* 'Mixed' Sample Threshold: is the number of markers with >= 2 alleles allowed before a sample is flagged for potential mixing. [default: 3]  
* Similarity Score Filter: is the similiarity score used for result filtering. [default: Tanabe]
* Similarity Score Filter Threshold: is the threshold to filter results. Only those samples with >= the threshold will appear in results. [default: 80]

## Batch Query Specific

`STRprofiler Database` and `Within File` options: 

* Amelogenin scoring is excluded by default but can be included by selecting the option.
* Tanabe Filter Threshold: is the Tanabe score threshold over which a sample is considered a match in batch and file queries. [default: 80] 
* Masters (vs. query) Filter Threshold: is the Masters (vs. query) score threshold over which a sample is considered a match in batch and file queries. [default: 80]
* Masters (vs. reference) Filter Threshold: is the Masters (vs. reference) score threshold over which a sample is considered a match in batch and file queries. [default: 80]

`Cellosaurus Database (CLASTR)` options:

* Similarity Score Filter: is the similiarity score used for result filtering. [default: Tanabe]
* Similarity Score Filter Threshold: is the threshold to filter results. Only those samples with >= the threshold will appear in results. [default: 80]

---

# Python Package & CLI

**STRprofiler** also has a command line interface through a python package available from [PyPI](https://pypi.org/project/strprofiler/).
The full docs are available on [ReadTheDocs](https://strprofiler.readthedocs.io/en/latest/).

---

# References

`STRprofiler` is provided under the MIT license. If you use this app in your research, please cite:    
Jared M Andrews, Michael W Lloyd, Steven B Neuhauser, Margaret Bundy, Emily L Jocoy, Susan D Airhart, Carol J Bult, Yvonne A Evrard, Jeffrey H Chuang, Suzanne Baker, STRprofiler: efficient comparisons of short tandem repeat profiles for biomedical model authentication, Bioinformatics, 2024;, btae713,<a href="https://doi.org/10.1093/bioinformatics/btae713" target="_blank">https://doi.org/10.1093/bioinformatics/btae713</a>

If you use the `strprofiler clastr` command or Cellosaurus database in the app, please cite:

Bairoch A. (2018) The Cellosaurus, a cell line knowledge resource. Journal of Biomolecular Techniques. 29:25-38. DOI: 10.7171/jbt.18-2902-002; PMID: 29805321 

Robin, T., Capes-Davis, A. & Bairoch, A. (2019) CLASTR: the Cellosaurus STR Similarity Search Tool - A Precious Help for Cell Line Authentication. International Journal of Cancer. PubMed: 31444973  DOI: 10.1002/IJC.32639
