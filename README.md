# strprofiler
 **strprofiler** is a simple python utility to compare short tandem repeat (STR) profiles. In particular, it is designed to aid research labs in comparing models (e.g. cell lines & xenografts) generated from primary tissue samples to ensure contamination has not occurred. It includes basic checks for sample mixing and contamination.

For each STR profile provided, **strprofiler** will generate a sample-specific report that includes the following similarity scores as compared to every other profile:

[Tanabe, AKA the Sørenson-Dice coefficient](https://www.doi.org/10.11418/jtca1981.18.4_329):

$$ score = \frac{2 * no.shared.alleles}{no.query.alleles + no.reference.alleles} $$

[Masters (vs. query)](https://www.ncbi.nlm.nih.gov/pubmed/11416159): 

$$ score = \frac{no.shared.alleles}{no.query.alleles} $$

[Masters (vs. reference)](https://www.ncbi.nlm.nih.gov/pubmed/11416159): 

$$ score = \frac{no.shared.alleles}{no.reference.alleles} $$

Amelogenin is not included in the score computation by default but can be included by passing the `--score_amel` flag.

## Installation

strprofiler is available on PyPI and can be installed with pip:

```bash
pip install strprofiler
```

## Usage

**strprofiler** can be run from the command line. Full usage information can be found by running `strprofiler --help`.



```bash
Usage: strprofiler [OPTIONS] INPUT_FILES...                                                                                                                                                                                    

STRprofiler compares STR profiles to each other.                            
                                                                                                                                                                                                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --tan_threshold    -tanth   FLOAT        Minimum Tanabe score to report as potential matches in summary table. [default: 80]                                                                                                                                      │
│ --mas_q_threshold  -masqth  FLOAT        Minimum Masters (vs. query) score to report as potential matches in summary table. [default: 80]                                                                                                                         │
│ --mas_r_threshold  -masrth  FLOAT        Minimum Masters (vs. reference) score to report as potential matches in summary table. [default: 80]                                                                                                                     │
│ --mix_threshold    -mix     INTEGER      Number of markers with >= 2 alleles allowed before a sample is flagged for potential mixing. [default: 3]                                                                                                                │
│ --fmt              -f       [long|wide]  Format of STR profile(s). Can be 'long' or 'wide'.  If 'long', all columns except the sample column are presumed to be markers. [default: long]                                                                          │
│ --sample_map       -sm      PATH         Path to sample map for renaming.                                                                                                                                                                                         │
│ --amel_col         -acol    TEXT         Name of Amelogenin column in STR file(s). Excluded form scoring. [default: AMEL]                                                                                                                                         │
│ --sample_col       -scol    TEXT         Name of sample column in STR file(s). [default: Sample]                                                                                                                                                                  │
│ --marker_col       -mcol    TEXT         Name of marker column in STR file(s). Only used if format is 'wide'. [default: Marker]                                                                                                                                   │
│ --penta_fix        -pfix                 Whether to try to harmonize PentaE/D allele spelling. [default: True]                                                                                                                                                    │
│ --score_amel       -amel                 Use Amelogenin for scoring. [default: False]                                                                                                                                                                             │
│ --output_dir       -o       PATH         Path to the output directory. [default: ./STRprofiler]                                                                                                                                                                   │
│ --version                                Show the version and exit.                                                                                                                                                                                               │
│ --help                                   Show this message and exit.        
```
