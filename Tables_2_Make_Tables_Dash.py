from os.path import join
import traceback
import json
from config.MainConfig import get_op_config
from config.params import WorldLitter
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import plotly.graph_objs as go
import numpy as np


config = get_op_config()
input_file = join(config[WorldLitter.output_folder_web], 'ReachedTablesData.json')
print(input_file)
with open(input_file) as f:
    data = json.load(f)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

def dashPlotTable(country_name,  to_data, from_data, id='1', type_plot='Table'):

    rows = []
    if type_plot == "Table":
        for i in range(max(len(from_data), len(to_data))):
            if i < len(from_data['from']) and i < len(to_data['to']):
                from_i = from_data['from'][i]
                to_i = to_data['to'][i]
                rows.append({"col1": F"{int(from_i['tons'])}, {from_i['perc']}% to {from_i['name']}",
                            "col2": F"{int(to_i['tons'])}, {to_i['perc']}% to {to_i['name']}"},)
            else:
                if i < len(from_data['from']):
                    from_i = from_data['from'][i]
                    rows.append({"col1": F"{int(from_i['tons'])} tons, {from_i['perc']}% to {from_i['name']}"})
                if i < len(to_data['to']):
                    to_i = to_data['to'][i]
                    rows.append({"col2": F"{int(to_i['tons'])} tons, {to_i['perc']}% from {to_i['name']}"})

            this_plot = dash_table.DataTable(id=F'table_{id}',
                                     columns=[{"name": F"From {country_name.capitalize()} ({from_data['tot_tons']})", "id": 'col1'},
                                              {"name": F"To {country_name.capitalize()} ({to_data['tot_tons']})", "id": 'col2'}],
                                     data=rows,
                                      style_cell_conditional=[
                                          {
                                              'if': {'column_id': c},
                                              'textAlign': 'left'
                                          } for c in ['Date', 'Region']
                                      ],
                                      style_data_conditional=[
                                          {
                                              'if': {'row_index': 'odd'},
                                              'backgroundColor': 'rgb(248, 248, 248)'
                                          }
                                      ],
                                      style_header={
                                          'backgroundColor': 'rgb(230, 230, 230)',
                                          'fontWeight': 'bold'
                                      }
                                              )
    else:
        x_to = []
        y_to = []
        x_from = []
        y_from = []
        for i in range(0, len(from_data)):
            from_i = from_data['from'][i]
            x_from.append(from_i['name'])
            y_from.append(int(from_i['tons']))

        for i in range(0, len(to_data)):
            to_i = to_data['to'][i]
            x_to.append(to_i['name'])
            y_to.append(int(to_i['tons']))

        trace1 = go.Bar(x=x_from, y=y_from)
        trace2 = go.Bar(x=x_to, y=y_to)

        this_plot = dbc.Row([
                        dbc.Col([
                            dcc.Graph(
                                id=F'plot_{id}',
                                figure={
                                    'data': [trace1],
                                    'layout':
                                        go.Layout(title=F" Waste from {country_name.capitalize()}",
                                                  height=300, yaxis={'title':'Tons per year'})
                                })
                            ], width=6),
                        dbc.Col([
                            dcc.Graph(
                                id=F'plot_to_{id}',
                                figure={
                                    'data': [trace2],
                                    'layout':
                                        go.Layout(title=F" Waste towards {country_name.capitalize()}",
                                                  height=300, yaxis={'title':'Tons per year'})
                                })
                        ], width=6),
                        ])

    return this_plot

def makeTables(data):
    tables = []
    for i, country_name in enumerate(np.array(sorted(data.keys()))[0:10]):
        try:
            to_data = data[country_name]['to']
            from_data = data[country_name]['from']
            current_table = dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H5(children=F"{country_name.capitalize()} exports {from_data['tot_tons']} tons per year")
                    ])
                ], className="text-center"),
                dbc.Row([
                    dbc.Col([
                        html.H6(children=F"{int(from_data['ocean_tons'])} ({from_data['ocean_perc']}%) end up on the ocean")]
                        , width=12),
                ], className="text-center"),
                dbc.Row([
                    dbc.Col([
                        html.H6(children=F"{int(from_data['beach_tons'])} ({from_data['beach_perc']}%) end up on the beach")],
                        width=12)
                ], className="text-center"),
                dbc.Row([
                    dbc.Col([
                        dashPlotTable(country_name, to_data, from_data, F'{i}'),
                    ], width=12),
                    dbc.Col([
                        dashPlotTable(country_name, to_data, from_data, F'{i}', 'plot'),
                    ], width=12)
                ], className='justify-content-md-center'),
                dbc.Row([
                    dbc.Col([
                        html.Hr()
                    ], width=12)
                ], className='justify-content-md-center')

            ])

            tables.append(current_table)
        except Exception as e:
            print(F"Failed for country: {country_name}: {traceback.print_exc()}")
    return tables

tables = makeTables(data)
app.layout = html.Div(tables)

print(help(dcc.Dropdown))

if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=False, port=8053, host='146.201.212.214') # COAPS
