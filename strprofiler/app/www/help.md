---
title: "STR Similarity"
subtitle: 'This site and tool are intended research purposes only'
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
For a provided sample entered manually in the `Database Query` or sample(s) uploaded from a batch file (Batch Database Query tab)
`STR Similarity` will generate a report that includes the similarity scores (described below) as computed against a database of known STR profiles.  
</p>
The report will differ depending on if an individual sample or batch of samples is provided.   

### Database information
Data underlying the database were provided by ..... `TO BE FILLED LATER AS DATABASE IS MADE.`   

---

### Individual Sample Report
For individual samples, a report is generated with the following fields.

| Output Field | Description |
| :--- |    :----   |
| Mixed Sample      | Flag to indicate sample mixing. Sample mixing is determined by the "'Mixed' Sample Threshold" option. If more markers are tri+ allelic than the threshold, samples are flagged as potentially mixed. |
| Shared Markers   | Number of markers shared between the query and database sample. |
| Shared Alleles   | Number of alleles shared between the query and database sample. |
| Tanabe Score | Tanabe similarity score between the query and database sample. |
| Master Query Score | Master 'Query' similarity score between the query and database sample. |
| Master Ref Score | Master 'Reference' similarity score between the query and database sample. |

---

### Batch Sample Report 
For batched samples, a report is summary report is generated. For individual sample comparison report, enter the individual sample in the database query tab.

| Output Field | Description |
| :---        |    :----   |
| Mixed Sample | Flag to indicate sample mixing. Sample mixing is determined by the "'Mixed' Sample Threshold" option. If more markers are tri+ 
| Top Match |	Name and Tanabe score of top match to sample. |
| Next Best Match |	Name and Tanabe score of next best match to sample. |
| Tanabe Matches | Name and Tanabe score of matches above scoring threshold to sample. |
| Master Query Matches | Name and Masters (vs. query) score of matches above scoring threshold to sample. |
| Master Ref Matches | Name and Masters (vs. reference) score of matches above scoring threshold to sample. |

---

# Non-database Queries
For batch samples entered in the File Query tab, `STR Similarity` will generate a report that mirrors the batch query above, except that samples will be queried against each other rather than against the database. 

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

### All fields

* Amelogenin is included in the score computation by default but can be excluded by de-selecting option.
* 'Mixed' Sample Threshold

### Batch and file specfic

* Tanabe Filter Threshold: is the Tanabe score threshold over which a sample is considered a match in batch and file queries. 
* Masters (vs. query) Filter Threshold: is the Masters (vs. query) score threshold over which a sample is considered a match in batch and file queries.
* Masters (vs. reference) Filter Threshold: is the Masters (vs. reference) score threshold over which a sample is considered a match in batch and file queries.

---

# Authors
<a href="https://github.com/MikeWLloyd" target="_blank">Mike Lloyd</a>, The Jackson Laboratory.  
<a href="https://github.com/j-andrews7" target="_blank">Jared Andrews</a>, St. Jude Children's Research Hospital

---

# License 
STR Similarity is provided under the MIT license. Source code can be found at <a href="https://github.com/MikeWLloyd/strprofiler_shiny/" target="_blank">MikeWLloyd/strprofiler_shiny</a>

---

# Citations
STR similarity relies on the python package <a href="https://pypi.org/project/strprofiler/" target="_blank">`strprofiler`</a> for file parsing and similarity score calculations.

> `strprofiler` is released under the MIT license:    
> Jared Andrews, & Sam Culley. (2022). <a href="https://github.com/j-andrews7/strprofiler" target="_blank">j-andrews7/strprofiler</a>: v0.1.3. Zenodo. <a href="https://doi.org/10.5281/zenodo.10463015" target="_blank">https://doi.org/10.5281/zenodo.10463015</a>


