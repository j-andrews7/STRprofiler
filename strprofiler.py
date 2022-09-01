import pandas as pd
import rich_click as click
from pathlib import Path
from datetime import datetime

def str_ingress(paths, f_format, sample_col, marker_col, sample_map=None):
    """
    Reads in a list of paths and returns a pandas DataFrame of STR alleles in long format.
    """

    samps_dicts = []

    for path in paths:
        if path.suffix == '.xlsx':
            df = pd.read_excel(path)
        elif path.suffix == '.csv':
            df = pd.read_csv(path)
        elif path.suffix == '.tsv':
            df = pd.read_csv(path, sep='\t')
        elif path.suffix == '.txt':
            df = pd.read_csv(path, sep='\t')
        
        df = df.applymap(lambda x: x.strip() if type(x)==str else x)

        df.columns = df.columns.str.strip()

        # Collapse allele columns for each marker into a single column if in wide format.
        df['Alleles'] = df.filter(like='Allele').apply(lambda x: ','.join([str(y) for y in x]), axis=1).str.strip(",").str.strip("nan").str.strip(",")

        # Group and collect dict from each sample for markers and alleles.
        grouped = df.groupby(sample_col)

        for samp in grouped.groups.keys():
            samp_df = grouped.get_group(samp)
            samps_dict = samp_df.set_index(marker_col).to_dict()["Alleles"]
            samps_dict["Sample"] = samp
            
            samps_dicts.append(samps_dict)

    allele_df = pd.DataFrame(samps_dicts)
    
    # Replace sample names with sample map if provided.
    if sample_map is not None:
        for id in sample_map.iloc[:, 0]:
            allele_df.loc[allele_df["Sample"] == id, sample_col] = sample_map.iloc[:,1][sample_map.iloc[:,0] == id].to_string(header=False, index=False)
    
    return allele_df

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-su", "--summary", help="", type=click.Path())
@click.option("-tanth", "--tan_threshold", default=80, 
              help="Minimum Tanabe score to report as potential matches in summary table.", 
              show_default=True, type=float)
@click.option("-masth", "--mas_threshold", default=80, 
              help="Minimum Masters (vs. query) score to report as potential matches in summary table.", 
              show_default=True, type=float)
@click.option("-f", "--fmt", 
              help="""Format of STR profile(s). Can be 'long' or 'wide'. 
              If 'long', all columns except the sample column are presumed to be markers.""", 
              default = "long", show_default=True, 
              type=click.Choice(['long', 'wide'], case_sensitive=False))
@click.option("-sm", "--sample_map", help="Path to sample map for renaming.", type=click.Path())
@click.option("-acol", "--amel_col", help="Name of Amelogenin column in STR file(s). Excluded form scoring.", 
              default = "Amel", show_default=True, type=str)
@click.option("-scol", "--sample_col", help="Name of sample column in STR file(s).", 
              default = "Sample Name", show_default=True, type=str)
@click.option("-mcol", "--marker_col", help="Name of marker column in STR file(s).", 
              default = "Marker", show_default=True, type=str)
@click.option("-o", "--output_dir", default="./STRprofiler", 
              help="Path to the output directory.", show_default=True, type=click.Path())
@click.argument("strs", help="", required=True, type=click.Path(exists=True), nargs = -1)
@click.version_option()
def strprofiler(strs, summary, output_dir, tan_threshold, mas_threshold, fmt, amel_col, 
                sample_map, sample_col, marker_col):
    """STRprofiler compares STR profiles to each other."""

    # Make output directory and open file for logging.
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d.%H_%M_%S")
    log_file = open(
        Path(output_dir, "strprofiler." + dt_string + ".log"), "w")

    print("STR profiles summary: " + summary, file=log_file)
    print("Tan threshold: " + str(tan_threshold), file=log_file)
    print("Mas threshold: " + str(mas_threshold), file=log_file)
    print("Format: " + fmt, file=log_file)
    print("Sample map: " + sample_map, file=log_file)
    print("Amelogenin column: " + amel_col, file=log_file)
    print("Sample column: " + sample_col, file=log_file)
    print("Marker column: " + marker_col, file=log_file)
    
    log_file.close()