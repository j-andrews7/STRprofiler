import rich_click as click
from strprofiler.strprofiler import strprofiler, app
from strprofiler.clastr import clastr_query

@click.group()
@click.version_option()
def cli():
    pass

cli.add_command(strprofiler)
cli.add_command(app)
cli.add_command(clastr_query)