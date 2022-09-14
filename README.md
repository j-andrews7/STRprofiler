# strprofiler
 **strprofiler** is a simple python utility to compare short tandem repeat (STR) profiles. In particular, it is designed to aid research labs in comparing models (e.g. cell lines & xenografts) generated from primary tissue samples to ensure contamination has not occurred. It includes basic checks for sample mixing and contamination.

For each STR profile provided, **strprofiler** will generate a sample-specific report that includes the following similarity scores as compared to every other profile:

Tanabe, AKA the Sørenson-Dice coefficient: 

$$ \frac{2 * #_shared_alleles}{#_query_alleles + #_reference_alleles} $$

## Installation

strprofiler is available on PyPI and can be installed with pip:

```bash
pip install strprofiler
```

## Usage


