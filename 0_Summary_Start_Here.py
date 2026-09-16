"""Local WorldLitter guide with commands to copy and run in a terminal.

Run with the existing environment:
    source /home/olmozavala/uv/envs/aieoas/bin/activate
    python 0_Summary_Start_Here.py --port 8060

Open http://127.0.0.1:8060. Requires Dash >= 3.4, NumPy, netCDF4, and Plotly.
The page reads mounted NetCDF inputs and copies commands; it executes no shell commands.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional, Tuple, TypedDict

from dash import Dash, Input, Output, State, ctx, dcc, html
from plotly.graph_objects import Figure
from utils.hycom_preview import FolderCatalog, discover_folders, list_netcdf_files, load_preview, field_figures, empty_figure


class DropdownOption(TypedDict):
    """String label/value pair serialized by Dash dropdown components."""

    label: str
    value: str


class FieldSelection(TypedDict):
    """JSON store payload connecting file navigation to the plotting callback."""

    folder: str
    filename: str


# Outputs follow select_file's decorator order: options, value, three disabled
# flags, position/status messages, and the selected-field store payload.
FileNavigation = Tuple[
    List[DropdownOption], Optional[str], bool, bool, bool, str, str,
    Optional[FieldSelection],
]


SSH_HOST = "ozavala@skynet.coaps.fsu.edu"
REMOTE = f"{SSH_HOST}:/nexsan"
MOUNT_POINT = Path("/nexsan")
CURRENTS_PATH = MOUNT_POINT / "people/xbxu/HYCOM/GLBv0.08"
MOUNT_COMMAND = f"sudo sshfs {REMOTE} {MOUNT_POINT}/"


app = Dash(__name__, title="WorldLitter · Start here")
app.index_string = """<!DOCTYPE html>
<html><head>{%metas%}<title>{%title%}</title>{%favicon%}{%css%}
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f6f7;color:#173747;
font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1200px;margin:60px auto;padding:0 24px}header{margin-bottom:32px}
.eyebrow{font-size:12px;letter-spacing:2px;color:#007d80;font-weight:700}
h1{font-size:40px;letter-spacing:-1.4px;margin:10px 0}header p{color:#536d7b}
.card{background:white;border:1px solid #d8e3e7;border-radius:0 0 14px 14px;padding:32px}
h2{font-size:23px;margin:0 0 16px}p{line-height:1.7}.path{display:block;
background:#edf5f5;padding:17px;border-radius:8px;color:#126a70;overflow-wrap:anywhere;
font:15px/1.6 ui-monospace,monospace;margin:20px 0}.remote{font-size:13px;color:#536d7b;
overflow-wrap:anywhere}.button{display:inline-block;margin-top:12px;background:#007d80;color:white;border:0;
border-radius:7px;padding:13px 22px;font:600 15px system-ui;cursor:pointer}
.button:hover{background:#00666a}.button:disabled{opacity:.6;cursor:wait}
.button:focus-visible{outline:3px solid #d58b30;outline-offset:3px}
.command{white-space:pre-wrap;overflow-wrap:anywhere;background:#173747;color:#f1fafb;
padding:18px;border-radius:8px;font:14px/1.7 ui-monospace,monospace;user-select:all}
.footnote{font-size:12px;color:#647a86;margin-top:20px}
.folder-guide{margin-top:26px;padding:20px 24px;background:#edf5f5;border-radius:8px}
.folder-guide h3{margin:0 0 12px;font-size:18px}.folder-guide li{line-height:1.8}
.folder-guide p:last-child{margin-bottom:0}
.viewer{border-top:1px solid #d8e3e7;margin-top:32px;padding-top:32px}
.selectors{display:grid;grid-template-columns:1fr 2fr;gap:18px;margin:20px 0}
label{display:block;font-size:14px;font-weight:600;margin-bottom:8px}
.file-select{margin:18px 0}.navigation{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.navigation .button{margin:0}.message{font-size:14px;color:#536d7b;line-height:1.7;overflow-wrap:anywhere}
.plots{margin-top:24px}.plots .dash-graph{margin-top:16px}
@media(max-width:600px){.selectors{grid-template-columns:1fr}}
@media(max-width:600px){main{margin:28px auto;padding:0 16px}.card{padding:23px}h1{font-size:32px}}
</style></head><body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body></html>"""

app.layout = html.Main([
    html.Header([
        html.Div("WORLDLITTER / PROJECT GUIDE", className="eyebrow"),
        html.H1("Start here"),
        html.P("Prepare your data and run the project, step by step."),
    ]),
    dcc.Tabs(id="guide-tabs", value="local-run", children=[
        dcc.Tab(label="Local Run", value="local-run",
                selected_style={"borderTop": "3px solid #007d80", "color": "#007d80",
                                "backgroundColor": "white", "fontWeight": "600"},
                children=html.Section([
                    html.H2("1. Connect to the ocean currents"),
                    html.P("The HYCOM ocean currents are stored on nexsan. "
                           "Mount the remote storage to make them available at this local path:"),
                    html.Code(str(CURRENTS_PATH), className="path"),
                    html.Div(f"{REMOTE} → {MOUNT_POINT}", className="remote"),
                    html.P("Copy this command, paste it into your terminal, and run it:"),
                    html.Pre(html.Code(MOUNT_COMMAND), id="mount-command", className="command"),
                    html.P(["Hint: ", html.Code("@linux")], className="footnote"),
                    dcc.Clipboard(
                        target_id="mount-command", id="copy-mount-command",
                        title="Copy command", children="Copy command",
                        copied_children="Copied!", className="button",
                    ),
                    html.P("You can also select the command above and copy it manually.",
                           className="footnote"),
                    html.Div([
                        html.H3("Which forcing folder should I use?"),
                        html.P("Each folder name begins with a year. Its suffix identifies "
                               "the velocity fields it contains:"),
                        html.Ul([
                            html.Li([html.Code("YEAR"), " — ocean currents only (for example, 2010)."]),
                            html.Li([html.Code("YEARc"), " — ocean currents + 0.01 × wind velocity "
                                     "(a 1% wind contribution; for example, 2010c)."]),
                            html.Li([html.Code("YEARw"), " — wind velocity only (for example, 2010w)."]),
                        ]),
                        html.P([html.Strong("Use YEARc for the intended runs with currents and a 1% wind contribution. "),
                                "These files already contain the combined velocity, so the wind "
                                "contribution should not be added a second time."]),
                    ], className="folder-guide"),
                    html.Div([
                        html.H2("2. Explore the velocity fields"),
                        html.P("Choose a year, a forcing folder, and a NetCDF file to inspect "
                               "velocity and relative vorticity around the Gulf of Mexico "
                               "(99°W–79°W, 18°N–32°N). Previous and Next move "
                               "through the files in the selected folder."),
                        html.Button("Refresh available years", id="refresh-years", n_clicks=0,
                                    className="button"),
                        dcc.Store(id="folder-catalog", data={}),
                        dcc.Store(id="selected-field"),
                        html.P(id="catalog-status", className="message", role="status"),
                        html.Div([
                            html.Div([html.Label("Year", htmlFor="year-selector"),
                                      dcc.Dropdown(id="year-selector", options=[], clearable=False,
                                                   placeholder="Select a year")]),
                            html.Div([html.Label("Forcing folder", htmlFor="folder-selector"),
                                      dcc.Dropdown(id="folder-selector", options=[], clearable=False,
                                                   placeholder="Select a folder")]),
                        ], className="selectors"),
                        html.Div([
                            html.Label("NetCDF file", htmlFor="file-selector"),
                            dcc.Dropdown(id="file-selector", options=[], clearable=False,
                                         searchable=True, placeholder="Select a NetCDF file"),
                        ], className="file-select"),
                        html.P(id="file-list-status", className="message", role="status"),
                        dcc.Loading(html.Div([
                            html.P(id="field-status", className="message", role="status"),
                            dcc.Graph(id="velocity-map", figure=empty_figure(),
                                      config={"displaylogo": False, "scrollZoom": True}),
                            dcc.Graph(id="vorticity-map", figure=empty_figure(),
                                      config={"displaylogo": False, "scrollZoom": True}),
                        ], className="plots"), type="circle", color="#007d80"),
                        html.Div([
                            html.Button("← Previous file", id="previous-file", n_clicks=0,
                                        disabled=True, className="button"),
                            html.Button("Next file →", id="next-file", n_clicks=0,
                                        disabled=True, className="button"),
                            html.Span(id="file-position", className="message"),
                        ], className="navigation"),
                        html.P("Velocity colors show speed in m/s; arrows show direction. "
                               "Vorticity is the vertical curl on a sphere, in 10⁻⁵ s⁻¹, "
                               "with no planetary rotation term. Positive values indicate "
                               "counterclockwise rotation. Gray areas have missing data. "
                               "Color limits use the 99th percentile within the Gulf for each file; "
                               "extreme values remain available on hover. Drag to zoom; "
                               "double-click to reset to the Gulf view.",
                               className="footnote"),
                    ], className="viewer"),
                ], className="card")),
    ]),
])


@app.callback(
    Output("folder-catalog", "data"), Output("year-selector", "options"),
    Output("year-selector", "value"), Output("catalog-status", "children"),
    Input("refresh-years", "n_clicks"), State("year-selector", "value"),
)
def refresh_years(
    _clicks: Optional[int],
    selected: Optional[str],
) -> Tuple[FolderCatalog, List[DropdownOption], Optional[str], str]:
    """Refresh mounted folders, retaining the selected year when available.

    Runs at page initialization and on Refresh. Missing/unreadable mounts clear
    the catalog and selection and provide a user-visible status message.
    """
    try:
        catalog = discover_folders(CURRENTS_PATH)
        years = sorted(catalog)
        value = selected if selected in years else (years[0] if years else None)
        message = (f"Found {len(years)} years and {sum(map(len, catalog.values()))} year-prefixed folders."
                   if years else "No year-prefixed folders found. Check the mounted currents path.")
        return catalog, [{"label": y, "value": y} for y in years], value, message
    except OSError as exc:
        return {}, [], None, f"Cannot read {CURRENTS_PATH}. Mount nexsan, then refresh. {exc}"


@app.callback(
    Output("folder-selector", "options"), Output("folder-selector", "value"),
    Input("year-selector", "value"), Input("folder-catalog", "data"),
)
def select_year(
    year: Optional[str],
    catalog: Optional[FolderCatalog],
) -> Tuple[List[DropdownOption], Optional[str]]:
    """Label forcing variants; prefer bare YEAR, otherwise the first folder.

    The explanatory text recommends YEARc for combined forcing, but this callback
    retains the existing currents-only default when a bare-year folder exists.
    """
    folders = (catalog or {}).get(year, [])
    labels = {"": "currents only", "c": "currents + 1% wind", "w": "wind only", "w+": "wind variant"}
    options = [{"label": f"{name} — {labels.get(name[4:], 'other forcing')}", "value": name}
               for name in folders]
    return options, year if year in folders else (folders[0] if folders else None)


@app.callback(
    Output("file-selector", "options"), Output("file-selector", "value"),
    Output("file-selector", "disabled"), Output("previous-file", "disabled"),
    Output("next-file", "disabled"), Output("file-position", "children"),
    Output("file-list-status", "children"),
    Output("selected-field", "data"),
    Input("folder-selector", "value"), Input("previous-file", "n_clicks"),
    Input("next-file", "n_clicks"), Input("file-selector", "value"),
    State("file-selector", "options"),
)
def select_file(
    folder: Optional[str],
    _previous: Optional[int],
    _next: Optional[int],
    selected: Optional[str],
    options: Optional[List[DropdownOption]],
) -> FileNavigation:
    """Select a file and synchronize navigation controls and the plot store.

    Folder changes rebuild the lexical file list and select its first entry.
    Previous/Next clamp at the boundaries; direct dropdown selection is retained.
    Dash callback context identifies the trigger, so click counts are unused.
    Empty folders and listing failures clear the selection and disable controls.
    """
    if not folder:
        return [], None, True, True, True, "", "Select an available year and folder.", None
    try:
        if ctx.triggered_id == "folder-selector" or not options:
            names = list_netcdf_files(CURRENTS_PATH, folder)
            options = [{"label": name, "value": name} for name in names]
            selected = names[0] if names else None
        else:
            names = [option["value"] for option in options]
        if not names:
            return [], None, True, True, True, "", f"No NetCDF files found in {folder}.", None
        index = names.index(selected) if selected in names else 0
        if ctx.triggered_id == "previous-file":
            index = max(0, index - 1)
        elif ctx.triggered_id == "next-file":
            index = min(len(names) - 1, index + 1)
        return (options, names[index], False, index == 0, index == len(names)-1,
                f"File {index+1:,} of {len(names):,}", f"{len(names):,} NetCDF files in {folder}, sorted by filename.",
                {"folder": folder, "filename": names[index]})
    except (OSError, ValueError) as exc:
        return [], None, True, True, True, "", f"Cannot list files: {exc}", None


@app.callback(
    Output("velocity-map", "figure"), Output("vorticity-map", "figure"),
    Output("field-status", "children"),
    Input("selected-field", "data"),
)
def display_file(selection: Optional[FieldSelection]) -> Tuple[Figure, Figure, str]:
    """Render the selected first surface record and a source/stride description.

    Empty selections or read/plot failures clear both maps so an earlier file
    cannot be mistaken for the current selection. File errors appear as status
    text; mounting remains a manual terminal action.
    """
    folder, filename = (selection or {}).get("folder"), (selection or {}).get("filename")
    if not filename or not folder:
        return empty_figure(), empty_figure(), ""
    try:
        data = load_preview(CURRENTS_PATH, folder, filename)
        velocity, vorticity = field_figures(data, folder)
        return velocity, vorticity, (
            f"{folder}/{filename} · Time: {data['time']} · "
            f"Record 1 of {data['records']} · Native grid {data['shape'][0]:,} × {data['shape'][1]:,}. "
            f"Vorticity computed on the native grid before cropping to the Gulf. "
            f"Display stride: {data['stride']} grid point(s)."
        )
    except Exception as exc:
        # A bad/unreadable file should not leave the previous file's maps visible.
        message = f"Could not display {filename}: {exc}"
        return empty_figure("File unavailable or unsupported."), empty_figure("File unavailable or unsupported."), message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8050, help="Local port (default: 8050)")
    args = parser.parse_args()
    app.run(host="127.0.0.1", port=args.port, debug=False)
