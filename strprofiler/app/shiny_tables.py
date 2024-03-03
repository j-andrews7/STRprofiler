# https://github.com/astrowonk/shiny_tables

from shiny import ui
from numpy import nan_to_num
import pandas as pd


def _clean_header_names(x):
    if isinstance(x, str):
        return x.replace("_", " ")
    return x


def process_header_style(col_name, header_style_dict, active=False):
    if not active:
        return
    style = ""
    if cell_style_entry := header_style_dict.get(col_name):
        if theStyle := cell_style_entry["style"]:
            return theStyle
    return None


def enhanced_from_dataframe(
    df,
    columns=None,
    link_column_suffix="_HREF",
    cell_style_dict=None,
    header_style_dict=None,
    float_format=".2f",
    index=False,
    index_label=None,
    date_format="%Y-%m-%d",
    header_callable=None,
    link_target=None,
    markdown_columns=None,
    column_callable_dict={},
    # process_header_classes=False,
    process_header_styles=False,
    className="table table-striped",
    style="width: 100%",  ## if true the cell style dict callable  will apply to header
    **table_kwargs,
):
    """make a shiny bootstrap table from a pandas dataframe but add hyperlinks based on matching column names. Conditionally style a column or columns

    cell_style_dict: dict of {column_name: {condition: style_dict}}

    condition can be astring or a function that returns a boolean

    if condition is a string, it must match the value of the column exactly.

    """
    if df.empty:
        return ui.tags.div()
    if index:
        df = df.reset_index()
        if index_label is not None:
            df = df.rename(columns={"index": index_label})

    if date_format is not None:
        for c in df.select_dtypes(["datetime"]).columns:
            df[c] = pd.to_datetime(df[c])

    if columns is not None:
        # needed in case columns keyword would otherwise remove  out the link column
        column_order_dict = {key: val for val, key in enumerate(columns)}
        columns = sorted(
            set(
                list(columns) + [f"{col + link_column_suffix}" for col in df.columns]
            ).intersection(set(df.columns)),
            key=lambda x: column_order_dict.get(x, float("inf")),
        )
    else:
        columns = df.columns
    data_dict = df.to_dict(orient="records")

    if cell_style_dict is None:
        cell_style_dict = {}

    if header_style_dict is None:
        header_style_dict = {}

    col_names = columns
    if header_callable is None:
        header_column_cells = [
            ui.tags.th(
                _clean_header_names(x),
                style=process_header_style(
                    x, header_style_dict=header_style_dict, active=process_header_styles
                ),
            )
            for x in col_names
            if not str(x).endswith(link_column_suffix)
        ]
    else:
        assert callable(header_callable), "header_callable must be callable"
        header_column_cells = [
            ui.tags.th(
                header_callable(_clean_header_names(x)),
                style=process_header_style(
                    x, header_style_dict, active=process_header_styles
                ),
            )
            for x in col_names
            if not str(x).endswith(link_column_suffix)
        ]

    table_header = [ui.tags.thead(ui.tags.tr(header_column_cells))]
    table_body = [
        ui.tags.tbody(
            [
                _make_row(
                    x,
                    col_names,
                    link_column_suffix,
                    cell_style_dict=cell_style_dict,
                    float_format=float_format,
                    date_format=date_format,
                    link_target=link_target,
                    markdown_columns=markdown_columns,
                    column_callable_dict=column_callable_dict,
                )
                for x in data_dict
            ]
        )
    ]

    return ui.tags.table(
        table_header + table_body, {"class": className, "style": style}
    )


def _make_row(
    data_dict_entry,
    col_names,
    link_column_suffix,
    cell_style_dict=None,
    float_format=".2f",
    date_format=None,
    link_target=None,
    button_columns=None,
    markdown_columns=None,
    column_callable_dict=None,
):
    if button_columns is None:
        button_columns = []
    if markdown_columns is None:
        markdown_columns = []

    if link_target is None:
        link_target = ""
    if cell_style_dict is None:
        cell_style_dict = {}

    def process_table_cell(
        col_name,
        link_names,
        column_callable_dict,
    ):
        """Add links to tables in the right way and handle nan strings."""
        shiny_style_class_dict = {}

        ## handle styles and classes
        if cell_style_entry := cell_style_dict.get(col_name):
            if isinstance(cell_style_entry, list):
                for item in cell_style_entry:
                    if data_dict_entry[col_name] in item[0]:
                        shiny_style_class_dict = item[1]

            elif callable(cell_style_entry):
                if theStyle := cell_style_entry(data_dict_entry[col_name]):
                    assert isinstance(
                        theStyle, dict
                    ), "cell_style Callable must return a dictionary"
                    shiny_style_class_dict = theStyle
            else:
                shiny_style_class_dict = {}

        # handle the content of the table cell itself

        if callable(cell_callablle := column_callable_dict.get(col_name)):
            return ui.tags.td(
                cell_callablle(
                    data_dict_entry, col_name
                )  ##need to be on the entire data_dict in case a tool tip or other functionality is
                # linked to data in the same row but on another column
            )

        # add auto hyperlinks based on another column
        if (thehref := f"{col_name}{link_column_suffix}") in link_names:
            if data_dict_entry[thehref].startswith("http"):
                return ui.tags.td(
                    ui.tags.a(
                        str(data_dict_entry[col_name]),
                        target=link_target,
                        href=str(
                            data_dict_entry[thehref],
                        ),
                    ),
                    shiny_style_class_dict,
                )
            return ui.tags.td(
                ui.tags.link(
                    str(data_dict_entry[col_name]),
                    href=str(data_dict_entry[thehref], shiny_style_class_dict),
                )
            )

        # markdown a column
        elif col_name in markdown_columns:
            return ui.tags.td(
                ui.markdown(data_dict_entry[col_name]),
            )

        # format folats and ints
        elif isinstance(data_dict_entry[col_name], float):
            return ui.tags.td(
                f"{nan_to_num(data_dict_entry[col_name]):{float_format}}",
                shiny_style_class_dict,
            )
        elif isinstance(data_dict_entry[col_name], int):
            return ui.tags.td(f"{data_dict_entry[col_name]:,}", shiny_style_class_dict)
        elif date_format and isinstance(data_dict_entry[col_name], pd.Timestamp):
            return ui.tags.td(
                data_dict_entry[col_name].strftime(date_format), shiny_style_class_dict
            )
        elif isinstance(data_dict_entry[col_name], str):
            return ui.tags.td(data_dict_entry[col_name], shiny_style_class_dict)
        return ui.tags.td(
            str(data_dict_entry[col_name]),
        )

    link_names = [x for x in col_names if str(x).endswith(link_column_suffix)]
    return ui.tags.tr(
        [
            process_table_cell(x, link_names, column_callable_dict=column_callable_dict)
            for x in col_names
            if not str(x).endswith(link_column_suffix)
        ]
    )
