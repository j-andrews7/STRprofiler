import pandas as pd
import rich_click as click
from pathlib import Path
from datetime import datetime

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-su", "--summary", help="", type=click.Path())
@click.option("-tanth", "--tan_threshold", default=80, help="", show_default=True, type=float)
@click.option("-masth", "--mas_threshold", default=80, help="", show_default=True, type=float)
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
    
    out_file.close()
    log_file.close()