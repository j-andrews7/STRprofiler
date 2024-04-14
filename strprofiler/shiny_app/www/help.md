---
title: "STRprofiler"
subtitle: 'This site and tool are intended for research purposes only.'
output: 
  html_document:
    theme: spacelab
    toc: true
    toc_float: true
    toc_depth: 4
    number_sections: false
    self_contained: true
---

# Database Queries  
For a provided sample entered manually in the `Database Single Query` or sample(s) uploaded from a batch file in the `Database Batch Query` tab, 
`STRprofiler` will generate a report that includes the similarity scores (described below) as computed against a database of known STR profiles.  
</p>
The report will differ depending on if an individual sample or batch of samples is provided.   

## Database information
Current data underlying the default database were provided by: [The Jackson Laboratory PDX program](https://tumor.informatics.jax.org/mtbwi/pdxSearch.do)  

---

## Database Single Query Report
For individual samples, a report is generated with the following fields.  

| Output Field | Description |
| :--- |    :----   |
| Mixed Sample      | Flag to indicate sample mixing. Sample mixing is determined by the "'Mixed' Sample Threshold" option. If more markers are tri+ allelic than the threshold, samples are flagged as potentially mixed. |
| Shared Markers   | Number of markers shared between the query and database sample. |
| Shared Alleles   | Number of alleles shared between the query and database sample. |
| Tanabe Score | Tanabe similarity score between the query and database sample. |
| Master Query Score | Master 'Query' similarity score between the query and database sample. |
| Master Ref Score | Master 'Reference' similarity score between the query and database sample. |

The report is filtered to include only those samples with greater than or equal to the `Similarity Score Filter Threshold` defined by the user.  

---

## Database Batch Query Report 
For batched samples, a report is summary report is generated. For individual sample comparison report, enter the individual sample in the database query tab.

| Output Field | Description |
| :---        |    :----   |
| Mixed Sample | Flag to indicate sample mixing. Sample mixing is determined by the "'Mixed' Sample Threshold" option. If more markers are tri+ 
| Top Match |	Name and Tanabe score of top match to sample. |
| Next Best Match |	Name and Tanabe score of next best match to sample. |
| Tanabe Matches | Name and Tanabe score of matches above scoring threshold to sample. |
| Master Query Matches | Name and Masters (vs. query) score of matches above scoring threshold to sample. |
| Master Ref Matches | Name and Masters (vs. reference) score of matches above scoring threshold to sample. |

The report is filtered to include only those samples with greater than or equal to the `Similarity Score Filter Thresholds` defined by the user.  

## Database File Managment

Users can upload custom database files. The files must be in CSV format. A 'Sample' header must be present, but custom marker names may be used. Note that to score `Amelogenin` using the option provided, there must be a `Amelogenin` header in the uploaded file.  


---

# Within File Query

For batch samples entered in the File Query tab, `STR Similarity` will generate a report that mirrors the batch query above, except that samples will be queried against each other rather than against the database. The report is filtered to include only those samples with greater than or equal to the `Similarity Score Filter Threshold` defined by the user.  


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

## Batch and File Query Specfic

* Amelogenin scoring is excluded by default but can be included by selecting the option.
* Tanabe Filter Threshold: is the Tanabe score threshold over which a sample is considered a match in batch and file queries. [default: 80] 
* Masters (vs. query) Filter Threshold: is the Masters (vs. query) score threshold over which a sample is considered a match in batch and file queries. [default: 80]
* Masters (vs. reference) Filter Threshold: is the Masters (vs. reference) score threshold over which a sample is considered a match in batch and file queries. [default: 80]

---

# Reference
`strprofiler` is provided under the MIT license. If you use this app in your research please cite:    
Jared Andrews, Mike Lloyd, & Sam Culley. (2024). <a href="https://github.com/j-andrews7/strprofiler" target="_blank">j-andrews7/strprofiler</a>: v0.1.4. Zenodo. <a href="https://doi.org/10.5281/zenodo.10544686" target="_blank">https://doi.org/10.5281/zenodo.10544686</a>