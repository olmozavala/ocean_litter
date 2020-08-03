from os.path import join
import json
from utils.several_utils import replace_names
from config.MainConfig import get_op_config
from config.params import WorldLitter
import numpy as np
from shapely.geometry import Polygon, Point, MultiPoint
from config.MainConfig import get_preproc_config
from config.params import WorldLitter, Preproc
import shapely.speedups
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

config = get_op_config()
input_file = join(config[WorldLitter.output_folder_web],'ReachedTablesData.json')
print(input_file)
with open(input_file) as f:
    data = json.load(f)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def makeToFromTable(country_name,  to_from_data, table_type='From', id='1'):

    if table_type=="From":
        rows = [{"col1":F"{x['tons']}, {x['perc']}% to {x['name']}"} for x in to_from_data[table_type.lower()]]
    else:
        rows = [{"col1":F"{x['tons']} tons, {x['perc']}% from {x['name']}"} for x in to_from_data[table_type.lower()]]

    this_table = html.Div([
        html.H3(F"{table_type} {country_name.capitalize()} (tons)"),
        dash_table.DataTable(id=F'table_{id}',
                             columns=[{"name": F"From {country_name}", "id": 'col1'}],
                             data=rows)
        ])
    return this_table

def makeTables(data):
    tables = []
    for country_name in data:
        to_data = data[country_name]['to']
        from_data = data[country_name]['from']
        current_table = [
            dbc.Container([
                dbc.Row(html.H1(children=F"{country_name.capitalize()} exports {from_data['tot_tons']} tons per year")),
                dbc.Row([
                    dbc.Col([
                        html.H4(children=F"{from_data['ocean_tons']} ({from_data['ocean_perc']}%) end up on the ocean")]
                        , width=2, className='bg-blue'),
                    dbc.Col([
                        html.H4(children=F"{from_data['beach_tons']} ({from_data['beach_perc']}%) end up on the ocean")],
                        width=2)
                ]),
                # dbc.Row([
                #     dbc.Col([
                #         html.Div([makeToFromTable(country_name, from_data, 'From', F'from_{country_name}'),
                #                   makeToFromTable(country_name, to_data, 'To', F'to_{country_name}')])
                #         ], width=12)
                #     ])
                ])
            ]
        return current_table

tables = makeTables(data)

app.layout = html.Div(tables)

print(help(dcc.Dropdown))

if __name__ == '__main__':
    app.run_server(debug=True)
