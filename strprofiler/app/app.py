import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo, ImgData
import pandas as pd

import strprofiler.strprofiler as sp
from strprofiler.app.calc_functions import _single_query, _batch_query, _file_query

from datetime import date
import time
import importlib.resources


def database_load(file):
    """
    Load a database from a file and return it as a dictionary.

    Args:
        file (str): Path to the database file.

    Returns:
        str_database: A dictionary of STR profiles in long format.

    Raises:
        Exception: If the file fails to load or if sample ID names are duplicated.
    """
    try:
        str_database = sp.str_ingress(
            [file],  # expects list
            sample_col="Sample",
            marker_col="Marker",
            sample_map=None,
            penta_fix=True,
        ).to_dict(orient="index")
    except Exception as e:
        m = ui.modal(
            ui.HTML(
                "The file failed to load.<br>Check if sample ID names are duplicated.<br><br>Reported error:<br>"
            ),
            ui.HTML(str(e) + "<br><br>"),
            ui.div(
                {"style": "font-size: 25px"},
                ui.HTML("Reloading stock database"),
            ),
            title="File Load Error",
            easy_close=True,
            footer=None,
        )
        ui.modal_show(m)

        f = importlib.resources.files("strprofiler.app")
        str_database = database_load(f.joinpath("www/jax_database.csv"))

    return str_database


def _highlight_non_matches(s):
    """
    Highlight the cells that do not match the first row's value in their respective columns.
    """
    is_match = s == s.iloc[0]
    return ["text-align:center;background-color:#ec7a80" if not v else "text-align:center" for v in is_match]

### App Generation ###

def create_app(db=None):

    f = importlib.resources.files("strprofiler.app")
    www_dir = str(f.joinpath("www"))

    if db is not None:
        init_db = database_load(db)
        init_db_name = db
    else:
        init_db = database_load(f.joinpath("www/jax_database.csv"))
        init_db_name = "jax_database.csv"

    stack = ui.HTML(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="currentColor"'
            ' class="bi bi-stack" viewBox="0 0 16 16"> <path d="m14.12 10.163 1.715.858c.22.11.22.424 0'
            " .534L8.267 15.34a.6.6 0 0 1-.534 0L.165 11.555a.299.299 0 0 1 0-.534l1.716-.858 5.317"
            " 2.659c.505.252 1.1.252 1.604 0l5.317-2.66zM7.733.063a.6.6 0 0 1 .534 0l7.568"
            " 3.784a.3.3 0 0 1 0 .535L8.267 8.165a.6.6 0 0 1-.534 0L.165 4.382a.299.299 0"
            ' 0 1 0-.535z"/> <path d="m14.12 6.576 1.715.858c.22.11.22.424 0 .534l-7.568'
            ' 3.784a.6.6 0 0 1-.534 0L.165 7.968a.299.299 0 0 1 0-.534l1.716-.858 5.317 2.659c.505.252 1.1.252 1.604 0z"/> </svg>'
        )
    )

    # TODO move this to a separate function
    app_ui = ui.page_fluid(
        ui.tags.style("#main {padding:12px !important} #sidebar {padding:12px}"),
        ui.tags.style(
            ".h3 {margin-bottom:0.1rem; line-height:1} .card-body {padding-top:6px; padding-bottom:6px}"
        ),
        ui.page_navbar(
            shinyswatch.theme.superhero(),
            ui.nav_menu(
                "Database Single/Batch Query",
                ui.nav_panel(
                    "Database Single Query",
                    ui.card(
                        ui.layout_sidebar(
                            ui.panel_sidebar(
                                {"id": "sidebar"},
                                ui.tags.h3("Options"),
                                ui.card(
                                    ui.input_switch(
                                        "score_amel_query", "Score Amelogenin", value=False
                                    ),
                                    ui.row(
                                        ui.column(
                                            6,
                                            ui.input_numeric(
                                                "mix_threshold_query",
                                                "'Mixed' Sample Threshold",
                                                value=3,
                                                width="100%",
                                            ),
                                        ),
                                        ui.column(
                                            6,
                                            ui.input_selectize(
                                                "query_filter",
                                                "Similarity Score Filter",
                                                choices=[
                                                    "Tanabe",
                                                    "Masters Query",
                                                    "Masters Reference",
                                                ],
                                                width="100%",
                                            ),
                                        ),
                                    ),
                                    ui.output_image(
                                        "image", height="50px", fill=True, inline=True
                                    ),
                                    ui.input_numeric(
                                        "query_filter_threshold",
                                        "Similarity Score Filter Threshold",
                                        value=80,
                                        width="100%",
                                    ),
                                ),
                                position="right",
                            ),
                            ui.panel_main(
                                {"id": "main"},
                                ui.column(
                                    12,
                                    ui.row(
                                        ui.column(4, ui.tags.h3("Sample Input")),
                                    ),
                                ),
                                ui.card(
                                    ui.column(
                                        12,
                                        ui.output_ui("marker_inputs"),
                                    ),
                                    full_screen=False,
                                    fill=False,
                                ),
                                ui.row(
                                    ui.column(
                                        4,
                                        ui.input_action_button(
                                            "demo_data",
                                            "Load Example Data",
                                            class_="btn-primary",
                                        ),
                                    ),
                                    ui.column(4, ui.output_ui("loaded_example_text")),
                                    ui.column(
                                        4,
                                        ui.input_action_button(
                                            "search",
                                            "Search",
                                            class_="btn-success",
                                            width="45%",
                                        ),
                                        ui.input_action_button(
                                            "reset",
                                            "Reset",
                                            class_="btn-danger",
                                            width="45%",
                                        ),
                                    ),
                                ),
                            ),
                        )
                    ),
                    ui.tags.hr(),
                    ui.card(
                        ui.row(
                            ui.column(3, ui.tags.h3("Results")),
                            ui.column(1, ui.p("")),
                        ),
                        ui.column(
                            12,
                            {"id": "res_card"},
                            ui.output_table("out_result"),
                        ),
                        full_screen=False,
                        fill=False,
                    ),
                ),
                ui.nav_panel(
                    "Database Batch Query",
                    ui.card(
                        ui.layout_sidebar(
                            ui.panel_sidebar(
                                {"id": "batch_sidebar"},
                                ui.tags.h3("Options"),
                                ui.tags.hr(),
                                ui.card(
                                    ui.input_switch(
                                        "score_amel_batch", "Score Amelogenin", value=False
                                    ),
                                    ui.input_numeric(
                                        "mix_threshold_batch",
                                        "'Mixed' Sample Threshold",
                                        value=3,
                                        width="100%",
                                    ),
                                    ui.input_numeric(
                                        "tan_threshold_batch",
                                        "Tanabe Filter Threshold",
                                        value=80,
                                        width="100%",
                                    ),
                                    ui.input_numeric(
                                        "mas_q_threshold_batch",
                                        "Masters (vs. query) Filter Threshold",
                                        value=80,
                                        width="100%",
                                    ),
                                    ui.input_numeric(
                                        "mas_r_threshold_batch",
                                        "Masters (vs. reference) Filter Threshold",
                                        value=80,
                                        width="100%",
                                    ),
                                ),
                                ui.input_file(
                                    "file1",
                                    "CSV Input File:",
                                    accept=[".csv"],
                                    multiple=False,
                                    width="100%",
                                ),
                                ui.input_action_button(
                                    "csv_query",
                                    "CSV Query",
                                    class_="btn-primary",
                                    width="100%",
                                ),
                                ui.download_button(
                                    "example_file1",
                                    "Download Example Batch File",
                                    class_="btn-secondary",
                                    width="100%",
                                ),
                                position="left",
                            ),
                            ui.panel_main(
                                ui.row(
                                    ui.column(3, ui.tags.h3("Results")),
                                    ui.column(6, ui.p("")),
                                ),
                                ui.column(
                                    12,
                                    {"id": "res_card_batch"},
                                    ui.output_data_frame("out_batch_df"),
                                    ui.p(""),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            ui.nav_panel(
                "Database File Managment",
                ui.layout_columns(
                    ui.value_box(
                        "Current Database:",
                        ui.div(
                            {"style": "font-size: 20px;"},
                            ui.output_text("current_db"),
                        ),
                        ui.output_text("sample_count"),
                        showcase=stack,
                        theme="bg-blue",
                        class_="font-size-10px",
                    ),
                    ui.hr(),
                    ui.output_ui("database_file"),
                    ui.input_action_button(
                        "reset_db", "Reset Custom Database", class_="btn-danger"
                    ),
                    col_widths=(-3, 6, -3),
                ),
            ),
            ui.nav_panel(
                "Within File Query",
                ui.card(
                    ui.layout_sidebar(
                        ui.panel_sidebar(
                            {"id": "novel_query_sidebar"},
                            ui.tags.h3("Options"),
                            ui.card(
                                ui.input_switch(
                                    "score_amel_file", "Score Amelogenin", value=False
                                ),
                                ui.input_numeric(
                                    "mix_threshold_file",
                                    "'Mixed' Sample Threshold",
                                    value=3,
                                    width="100%",
                                ),
                                ui.input_numeric(
                                    "tan_threshold_file",
                                    "Tanabe Filter Threshold",
                                    value=80,
                                    width="100%",
                                ),
                                ui.input_numeric(
                                    "mas_q_threshold_file",
                                    "Masters (vs. query) Filter Threshold",
                                    value=80,
                                    width="100%",
                                ),
                                ui.input_numeric(
                                    "mas_r_threshold_file",
                                    "Masters (vs. reference) Filter Threshold",
                                    value=80,
                                    width="100%",
                                ),
                            ),
                            ui.input_file(
                                "file2",
                                "CSV Input File:",
                                accept=[".csv"],
                                multiple=False,
                                width="100%",
                            ),
                            ui.input_action_button(
                                "csv_query2",
                                "CSV Query",
                                class_="btn-primary",
                                width="100%",
                            ),
                            ui.download_button(
                                "example_file2",
                                "Download Example Batch File",
                                class_="btn-secondary",
                                width="100%",
                            ),
                            position="left",
                        ),
                        ui.panel_main(
                            ui.row(
                                ui.column(3, ui.tags.h3("Results")),
                                ui.column(6, ui.p("")),
                            ),
                            ui.column(
                                12,
                                {"id": "res_card_file"},
                                ui.output_data_frame("out_file_df"),
                                ui.p(""),
                            ),
                        ),
                    ),
                ),
            ),
            ui.nav_panel(
                "About",
                ui.panel_main(
                    ui.tags.iframe(
                        src="help.html",
                        width="100%",
                        style="height: 85vh;",
                        scrolling="yes",
                        frameborder="0",
                    )
                ),
            ),
            title="strprofiler",
        ),
    )

    def server(input, output, session):

        file_check = reactive.value(False)
        reset_count = reactive.value(0)
        res_click = reactive.value(0)
        res_click_batch = reactive.value(0)
        res_click_file = reactive.value(0)
        str_database = reactive.value(init_db)
        db_name = reactive.value(init_db_name)
        output_df = reactive.value(None)
        demo_vals = reactive.value(None)
        demo_name = reactive.value(None)
        markers = reactive.value(list(init_db[next(iter(init_db))].keys()))

        @output
        @render.text
        def current_db():
            return db_name()

        @render.ui
        @reactive.event(file_check)
        def database_file():
            return ui.input_file(
                "database_upload",
                "Upload Custom Database",
                accept=[".csv"],
                multiple=False,
                width="100%",
            )

        @render.ui
        @reactive.event(markers)
        def marker_inputs():
            def _marker_ui(id):
                return ui.column(2, ui.input_text(id, id, placeholder=""))
            return ui.row([_marker_ui(marker) for marker in markers()])

        @reactive.effect
        @reactive.event(input.reset_db)
        def _():
            file_check.set(not file_check())
            str_database.set(init_db)
            db_name.set(init_db_name)
            markers.set(list(init_db[next(iter(init_db))].keys()))

            @output
            @render.text
            def current_db():
                return db_name()

            @reactive.Calc
            @render.text
            def sample_count():
                return "Number of Database Samples: " + str(len(str_database()))

        @reactive.effect
        @reactive.event(input.database_upload)
        def _():
            if input.database_upload():
                file: list[FileInfo] | None = input.database_upload()
            else:
                return
            str_database.set(database_load(file[0]["datapath"]))
            markers.set(list(str_database()[next(iter(str_database()))].keys()))

            @output
            @render.text
            def current_db():
                db_name.set(file[0]["name"])
                return db_name()

            @reactive.calc
            @render.text
            def sample_count():
                return "Number of Database Samples: " + str(len(str_database()))

        @reactive.calc
        @render.text
        def sample_count():
            return "Number of Database Samples: " + str(len(str_database()))

        ################
        # Single sample query
        @render.image
        def image():

            if input.query_filter() == "Tanabe":
                img: ImgData = {
                    "src": f.joinpath("www/tanabe_inverted.png"),
                    "width": "320px",
                    "height": "45px",
                }
                return img
            elif input.query_filter() == "Masters Query":
                img: ImgData = {
                    "src": f.joinpath("www/masters_query_inverted.png"),
                    "width": "200px",
                    "height": "45px",
                }
                return img
            elif input.query_filter() == "Masters Reference":
                img: ImgData = {
                    "src": f.joinpath("www/masters_ref_inverted.png"),
                    "width": "200px",
                    "height": "45px",
                }
                return img

        # Dealing with demo data load
        # Add some demo genotype information to the fields
        @reactive.effect
        @reactive.event(input.demo_data)
        def _():
            demo_name.set(next(iter(str_database())))
            demo_vals.set(str_database()[demo_name()])

            # Update the fields with the demo data using the marker list and demo_vals list
            for marker in markers():
                ui.update_text(marker, value=demo_vals()[marker])

            @output
            @render.text
            def loaded_example_text():
                x = ui.strong("Example: " + demo_name())
                return x

        # Reset all marker fields
        # Effect occurs on click of 'Reset Inputs' button
        @reactive.effect
        @reactive.event(input.reset)
        def reset_clicked():
            [ui.update_text(marker, value="") for marker in markers()]
            ui.update_switch("score_amel_query", value=False)
            ui.update_numeric("mix_threshold_query", value="3")

            @output
            @render.text
            def loaded_example_text():
                x = ui.strong("")
                return x

        # Dealing with calculating a results table
        # Catch when either reset or search is clicked
        # If reset, clear the query and run to make an empty df.
        # The empty df removes any existing table from the UI.
        # If search, populate with the query table, check if something
        # is actually in query, and then run single_query
        # If query has data, results are expected and
        # the download button is turned on. If query is empty,
        # no results are expected and download button removed.
        @reactive.calc
        @reactive.event(input.search, input.reset)
        def output_results():

            if input.reset() != reset_count():
                query = {m: "" for m in markers()}
            else:
                query = {m: input[m]() for m in markers()}

            reset_count.set(input.reset())
            if not any(query.values()):

                @output
                @render.text
                def loaded_example_text():
                    return ""

                ui.remove_ui("#inserted-downloader")
                res_click.set(0)
                return None
            if res_click() == 0:
                ui.insert_ui(
                    ui.div(
                        {"id": "inserted-downloader"},
                        ui.download_button(
                            "download", "Download CSV", width="25%", class_="btn-primary"
                        ),
                    ),
                    selector="#res_card",
                    where="afterEnd",
                )
                res_click.set(1)

            return _single_query(
                query,
                str_database(),
                input.score_amel_query(),
                input.mix_threshold_query(),
                input.query_filter(),
                input.query_filter_threshold(),
            )

        @output
        @render.table
        def out_result():
            output_df.set(output_results())

            if output_df() is not None:
                out_df = output_df().copy()
                out_df = out_df.style.set_table_attributes(
                    'class="dataframe shiny-table table w-auto"'
                ).hide(axis="index").apply(_highlight_non_matches, subset=out_df.columns[5:], axis=0).format(
                    {
                        "Shared Markers": "{0:0.0f}",
                        "Shared Alleles": "{0:0.0f}",
                        "Tanabe Score": "{0:0.2f}",
                        "Masters Query Score": "{0:0.2f}",
                        "Masters Ref Score": "{0:0.2f}",
                    },
                    na_rep=""
                )
            else:
                out_df = pd.DataFrame({"No input provided.": []})
            return out_df

        # Dealing with downloading results, when requested.
        # Note that output_results() is a reactive Calc result.
        @render.download(
            filename="STR_Query_Results_"
            + date.today().isoformat()
            + "-"
            + time.strftime("%Hh-%Mm", time.localtime())
            + ".csv"
        )
        def download():
            if output_results() is not None:
                yield output_results().to_csv(index=False)

        ################
        # CSV BATCH SECTION

        # On click of CSV Query, load file (or catch empty)
        # This effect catches any Calc change below (file loaded or not)
        # and if present uses the query DF as input to batch query.
        # Results are saved out to a file.
        @output
        @render.data_frame
        def out_batch_df():
            output_df.set(batch_query_results())
            try:
                return render.DataTable(output_df())
            except Exception:
                m = ui.modal(
                    ui.div(
                        {"style": "font-size: 18px"},
                        ui.HTML(
                            (
                                "There was a fatal error in the query.<br><br>"
                                "Ensure marker names match expectation, and that"
                                " no special characters (spaces, etc.) were used in sample names."
                            )
                        ),
                    ),
                    title="Batch Query Error",
                    easy_close=True,
                    footer=None,
                )
                ui.modal_show(m)
                return render.DataTable(pd.DataFrame({"Failed Query. Fix Input File": []}))

        # File input loading
        @reactive.calc
        @reactive.event(input.csv_query)
        def batch_query_results():

            file: list[FileInfo] | None = input.file1()
            if file is None:
                ui.remove_ui("#inserted-downloader2")
                return pd.DataFrame({"": []})
            query_df = sp.str_ingress(
                [file[0]["datapath"]],
                sample_col="Sample",
                marker_col="Marker",
                sample_map=None,
                penta_fix=True,
            ).to_dict(orient="index")

            if res_click_file() == 0:
                ui.insert_ui(
                    ui.div(
                        {"id": "inserted-downloader2"},
                        ui.download_button(
                            "download2", "Download CSV", width="25%", class_="btn-primary"
                        ),
                    ),
                    selector="#res_card_batch",
                    where="beforeEnd",
                )
                res_click_file.set(1)
            return _batch_query(
                query_df,
                str_database(),
                input.score_amel_batch(),
                input.mix_threshold_batch(),
                input.tan_threshold_batch(),
                input.mas_q_threshold_batch(),
                input.mas_r_threshold_batch(),
            )

        # Dealing with dowloading results, when requested.
        # Note that output_results() is a reactive Calc result.
        @render.download(
            filename="STR_Batch_Results_"
            + date.today().isoformat()
            + "_"
            + time.strftime("%Hh-%Mm", time.localtime())
            + ".csv"
        )
        def download2():
            if batch_query_results() is not None:
                yield batch_query_results().to_csv(index=False)

        # Dealing with passing example file to user.
        @render.download()
        def example_file1():
            path = str(f.joinpath("www/Example_Batch_File.csv"))
            return path

        ################
        # File many to many query

        # On click of CSV Query, load file (or catch empty)
        # This effect catches any Calc change below (file loaded or not)
        # and if present uses the query DF as input to batch query.
        # Results are saved out to a file.
        @output
        @render.data_frame
        def out_file_df():
            output_df.set(file_query_results())
            if output_df() is not None:
                return render.DataTable(output_df())

        # File input loading
        @reactive.calc
        @reactive.event(input.csv_query2)
        def file_query_results():

            file: list[FileInfo] | None = input.file2()
            if file is None:
                ui.remove_ui("#inserted-downloader3")
                return pd.DataFrame({"": []})
            query_df = sp.str_ingress(
                [file[0]["datapath"]],
                sample_col="Sample",
                marker_col="Marker",
                sample_map=None,
                penta_fix=True,
            ).to_dict(orient="index")

            if res_click_batch() == 0:
                ui.insert_ui(
                    ui.div(
                        {"id": "inserted-downloader3"},
                        ui.download_button(
                            "download3", "Download CSV", width="25%", class_="btn-primary"
                        ),
                    ),
                    selector="#res_card_file",
                    where="beforeEnd",
                )
                res_click_batch.set(1)
            return _file_query(
                query_df,
                input.score_amel_file(),
                input.mix_threshold_file(),
                input.tan_threshold_file(),
                input.mas_q_threshold_file(),
                input.mas_r_threshold_file(),
            )

        # Dealing with dowloading results, when requested.
        # Note that output_results() is a reactive Calc result.
        @render.download(
            filename="STR_Results_"
            + date.today().isoformat()
            + "_"
            + time.strftime("%Hh-%Mm", time.localtime())
            + ".csv"
        )
        def download3():
            if file_query_results() is not None:
                yield file_query_results().to_csv(index=False)

        # Dealing with passing example file to user.
        @render.download()
        def example_file2():
            path = str(f.joinpath("www/Example_Batch_File.csv"))
            return path

    app = App(app_ui, server, static_assets=www_dir)

    return app
