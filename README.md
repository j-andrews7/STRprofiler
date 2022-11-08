# strprofiler

[![Coverage Status](https://coveralls.io/repos/github/j-andrews7/strprofiler/badge.svg?branch=main)](https://coveralls.io/github/j-andrews7/strprofiler?branch=main)
[![PyPI version](https://badge.fury.io/py/strprofiler.svg)](https://badge.fury.io/py/strprofiler)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/strprofiler.svg)](https://pypi.python.org/pypi/strprofiler/)
[![PyPI license](https://img.shields.io/pypi/l/strprofiler.svg)](https://pypi.python.org/pypi/strprofiler/)

**strprofiler** is a simple python utility to compare short tandem repeat (STR) profiles. In particular, it is designed to aid research labs in comparing models (e.g. cell lines & xenografts) generated from primary tissue samples to ensure contamination has not occurred. It includes basic checks for sample mixing and contamination.

**strprofiler is intended only for research purposes.**

For each STR profile provided, **strprofiler** will generate a sample-specific report that includes the following similarity scores as compared to every other profile:

[Tanabe, AKA the Sørenson-Dice coefficient](https://www.doi.org/10.11418/jtca1981.18.4_329):

$$ score = \frac{2 * no.shared.alleles}{no.query.alleles + no.reference.alleles} $$

[Masters (vs. query)](https://www.ncbi.nlm.nih.gov/pubmed/11416159): 

$$ score = \frac{no.shared.alleles}{no.query.alleles} $$

[Masters (vs. reference)](https://www.ncbi.nlm.nih.gov/pubmed/11416159): 

$$ score = \frac{no.shared.alleles}{no.reference.alleles} $$

Amelogenin is not included in the score computation by default but can be included by passing the `--score_amel` flag.

## Installation

**strprofiler** is available on PyPI and can be installed with pip:

```bash
pip install strprofiler
```

## Usage

**strprofiler** can be run directly from the command line. 

`strprofiler -sm "SampleMap_exp.csv" -scol "Sample Name" -o ./strprofiler_output STR1.xlsx STR2.csv STR3.txt`

Full usage information can be found by running `strprofiler --help`.

```bash
 Usage: strprofiler [OPTIONS] INPUT_FILES...   

 STRprofiler compares STR profiles to each other.  

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --tan_threshold    -tanth   FLOAT        Minimum Tanabe score to report as potential matches in summary table. [default: 80]                          │
│ --mas_q_threshold  -masqth  FLOAT        Minimum Masters (vs. query) score to report as potential matches in summary table. [default: 80]             │
│ --mas_r_threshold  -masrth  FLOAT        Minimum Masters (vs. reference) score to report as potential matches in summary table. [default: 80]         │
│ --mix_threshold    -mix     INTEGER      Number of markers with >= 2 alleles allowed before a sample is flagged for potential mixing. [default: 3]    │
│ --sample_map       -sm      PATH         Path to sample map in csv format for renaming. First column should be sample names as given                  |
|                                            in STR file(s),  second should be new names to assign. No header.                                          │
│ --amel_col         -acol    TEXT         Name of Amelogenin column in STR file(s). [default: AMEL]                                                    │
│ --sample_col       -scol    TEXT         Name of sample column in STR file(s). [default: Sample]                                                      │
│ --marker_col       -mcol    TEXT         Name of marker column in STR file(s). Only used if format is 'wide'. [default: Marker]                       │
│ --penta_fix        -pfix                 Whether to try to harmonize PentaE/D allele spelling. [default: True]                                        │
│ --score_amel       -amel                 Use Amelogenin for similarity scoring. [default: False]                                                      │
│ --output_dir       -o       PATH         Path to the output directory. [default: ./STRprofiler]                                                       │
│ --version                                Show the version and exit.                                                                                   │
│ --help                                   Show this message and exit.                                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Input Files(s)

**strprofiler** can take either a single STR file or multiple STR files as input. These files can be csv, tsv, tab-separated text, or xlsx (first sheet used) files. The STR file(s) should be in either 'wide' or 'long' format. The long format expects all columns to map to the markers except for the designated sample name column with each row reflecting a different profile, e.g.:

| Sample | D1S1656 |  DYS391 | D3S1358 | D2S441 | D16S539 | D5S818 | D8S1179 | D22S1045 | D18S51 |
|:------:|:-------:|:-------:|:-------:|:------:|:-------:|:------:|:-------:|:--------:|:------:|
| Line1  |   12,14 |      12 |      13 |  12,14 |    17.3 |  16,17 |    18.3 |          |  17,11 |
| Line2  |   12,14 | 11.3,12 |   13,15 |  12,14 |    17.3 |  16,17 |    18.3 |          |  17,11 |
| ...    |         |         |         |        |         |        |         |          |        |

The wide format expects a line for each marker for each sample, e.g.:

|  Sample Name |   Marker  |  Allele   1 |  Size 1 |  Height   1 |  Allele   2 |  Size 2 |  Height   2 |  Allele   3 |
|:------------:|:---------:|:-----------:|:-------:|:-----------:|:-----------:|:-------:|:-----------:|:-----------:|
| Sample1      |  DYS391   |             |         |             |             |         |             |             |
| Sample1      |  D3S1358  | 16          | 128.29  | 8268        | 18          | 136.84  | 5467        | 16          |
| Sample1      |  D16S539  | 12          | 110.7   | 9660        | 13          | 115.17  | 5215        |             |
| Sample1      |  Penta D  | 9           | 415.04  | 5099        | 13          | 435.88  | 9426        |             |
| Sample1      |  D22S1045 | 15          | 455.95  | 13504       | 17          | 462.06  | 6186        |             |
| Sample1      |  Penta E  | 11          | 397.7   | 7420        | 14          | 412.02  | 5986        |             |
| Sample1      |  D18S51   | 12          | 153.72  | 9134        | 16          | 170.48  | 10501       |             |
| Sample1      |  D2S1338  | 20          | 263.91  | 3209        | 21          | 267.97  | 3834        |             |
| Sample1      |  TH01     | 7           | 85.33   | 8305        | 9.3         | 97.43   | 7853        |             |
| Sample1      |  D7S820   | 10          | 292.51  | 12340       | 14          | 308.71  | 11784       |             |
| Sample1      |  D12S391  | 15          | 141.53  | 12870       | 18.3        | 157.12  | 13731       |             |
| Sample1      |  AMEL     |  X          | 81.97   | 16696       |             |         |             |             |
| Sample1      |  D10S1248 | 16          | 283.82  | 8469        |             |         |             |             |
| Sample1      |  D13S317  | 12          | 328.21  | 7079        |             |         |             |             |
| Sample1      |  D21S11   | 32.2        | 239.67  | 19231       |             |         |             |             |
| Sample1      |  TPOX     | 11          | 424.02  | 12239       |             |         |             |             |
| Sample1      |  D19S433  | 14          | 228.37  | 14273       |             |         |             |             |
| Sample1      |  FGA      | 23          | 302.23  | 14599       |             |         |             |             |
| Sample2      |  D16S539  | 9           | 97.59   | 9286        | 11          | 106.43  | 8592        |             |
| Sample2      |  TH01     | 9.3         | 97.45   | 5920        |             |         |             |             |
| Sample2      |  D8S1179  | 13          | 101.1   | 26414       |             |         |             |             |
| Sample2      |  AMEL     |  X          | 82.1    | 7476        |  Y          | 88.34   | 8029        |             |
| Sample2      |  D3S1358  | 14          | 119.87  | 10146       | 15          | 124.14  | 10160       | 19          |
| Sample2      |  D18S51   | 12          | 153.8   | 9316        | 18          | 178.79  | 9182        | 19          |
| Sample2      |  Penta D  | 10          | 420.13  | 7693        | 11          | 425.25  | 7945        | 12          |
| Sample2      |  vWA      | 17          | 156.9   | 7953        | 18          | 160.86  | 8230        |             |
| Sample2      |  TPOX     | 9           | 416     | 6596        | 11          | 424.02  | 5304        |             |
| Sample2      |  D12S391  | 21          | 166.75  | 13481       | 22          | 170.9   | 14232       |             |
| Sample2      |  D22S1045 | 15          | 455.95  | 14310       | 17          | 462.06  | 10898       |             |
| Sample2      |  D2S441   | 14          | 236.24  | 18628       |             |         |             |             |
| Sample2      |  DYS391   | 10          | 468.83  | 6722        |             |         |             |             |
| Sample2      |  FGA      | 21          | 294.67  | 11941       |             |         |             |             |

In this format, the `marker_col` must be specified. Only columns beginning with "Allele" will be used to parse the alleles for each sample/marker. Any other size or height columns will be ignored.

## Output Files

**strprofiler** generates two types of output files. The first is a summary file, which contains the top hits for each sample above the specified scoring thresholds. This file provides a useful overview in addition to a flag to identify samples with potential mixing for closer inspection. In the output directory, this file will be named `full_summary.strprofiler.YYYYMMDD.HH_MM_SS.csv` where the date and time are the time the program was run.

In addition to the marker columns, the summary file contains the following columns:

| **Column Name**           | **Description**                                                                      |
|---------------------------|--------------------------------------------------------------------------------------|
| **mixed**                 | Flag to indicate sample mixing.                                                      |
| **top_hit**               | Name and Tanabe score of top match to sample.                                        |
| **next_best**             | Name and Tanabe score of next best match to sample.                                  |
| **tanabe_matches**        | Name and Tanabe score of matches above scoring threshold to sample.                  |
| **masters_query_matches** | Name and Masters (vs. query) score of matches above scoring threshold to sample.     |
| **masters_ref_matches**   | Name and Masters (vs. reference) score of matches above scoring threshold to sample. |

The second is a sample-specific comparison file, which contains the results of the comparison between the query sample and all other provided samples. These files are generated for each STR profile provided in the input file(s) and named after the query sample in question. For example, if the input file contains a sample named `Sample1`, the output file will be named `Sample1.strprofiler.YYYYMMDD.HH_MM_SS.csv`.

In addition to the marker columns, this output contains the following columns:

| **Column Name**         | **Description**                                              |
|-------------------------|--------------------------------------------------------------|
| **mixed**               | Flag to indicate sample mixing.                              |
| **query_sample**        | Flag to indicate query sample.                               |
| **n_shared_markers**    | Number of shared markers between query and reference sample. |
| **n_shared_alleles**    | Number of shared alleles between query and reference sample. |
| **n_query_alleles**     | Total number of alleles in query sample.                     |
| **n_reference_alleles** | Total number of alleles in reference sample.                 |
| **tanabe_score**        | Tanabe similarity score.                                     |
| **masters_query_score** | Masters (vs query) similarity score.                         |
| **masters_ref_score**   | Masters (vs reference) similarity score.                     |

## Contributing
You can contribute by creating [issues](https://github.com/j-andrews7/strprofiler/issues) to highlight bugs and make suggestions for additional features. [Pull requests](https://github.com/j-andrews7/strprofiler/pulls) are also very welcome.

## License

**strprofiler** is released on the MIT license. You are free to use, modify, or redistribute it in almost any way, provided you state changes to the code, disclose the source, and use the same license. It is released with zero warranty for any purpose and I retain no liability for its use. [Read the full license](https://github.com/j-andrews7/strprofiler/blob/master/LICENSE) for additional details.

