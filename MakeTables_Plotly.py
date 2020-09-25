from os.path import join
import traceback
import json
from config.MainConfig import get_op_config
from config.params import WorldLitter
import plotly.graph_objs as go
import numpy as np
import plotly.graph_objects as go

MAX_ROWS = 15
config = get_op_config()
input_file = join(config[WorldLitter.output_folder_web], 'ReachedTablesData.json')
print(input_file)
with open(input_file) as f:
    data = json.load(f)

def addRows(data, data_type):
    add_others = False
    others_val = 0
    others_perc = 0
    rows = []
    dir_text = "to" if data_type == "from" else "from"
    for i in range(0, len(data[data_type])):
        c_row = data[data_type][i]
        if i > MAX_ROWS:
            others_val += int(c_row['tons'])
            others_perc += c_row['perc']
            add_others = True
        else:
            if c_row['tons'] > 1:
                rows.append(F"{int(c_row['tons'])} tons {dir_text} {c_row['name']} ({c_row['perc']:0.1f}%) ")
            else:
                rows.append(F"Less than 1 ton {dir_text} {c_row['name']} ({c_row['perc']:0.1f}%) ")

    if add_others:
        if int(c_row['tons']) > 1:
            rows.append(F"{others_val} tons {dir_text} other countries ({others_perc:0.1f}%) ")
        else:
            rows.append(F"Less than 1 ton {dir_text} other countries ({others_perc:0.1f}%) ")

    return rows

def dashPlotTable(country_name,  to_data, from_data, title):

    headerColor = '#E6E6E6'
    rowEvenColor = '#F8F8F8'
    rowOddColor = 'white'

    rows_from = addRows(from_data, 'from')
    rows_to = addRows(to_data, 'to')

    fig = go.Figure(data=[go.Table(header=dict(values=[F"Waste from {country_name.capitalize()} ({from_data['tot_tons']} tons)",
                                                       F"Waste towards {country_name.capitalize()} ({to_data['tot_tons']} tons)"],
                                               fill_color=headerColor,
                                               line_color='gray',
                                               height=25),
                                   cells=dict(values=[rows_from, rows_to],
                                              fill_color=[[rowEvenColor if i % 2 == 1 else rowOddColor for i in range(len(rows_from))]],
                                              line_color='gray',
                                              height=25)
                                   )])
    fig.update_layout(width=700,
                      # height=200 + min(MAX_ROWS, max(len(from_data['from']), len(to_data['to'])))*25,
                      height=200 + MAX_ROWS*25,
                      margin=dict(
                          l=20, r=20, t=100, b=20
                      ),
                      title=dict(text=title,
                                            x=0.5,
                                            font=dict(
                                                size=16
                                            )),
                      )
    fig.write_image(F"/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/table_images/{country_name.replace(' ','_')}.png",
                    scale=2, engine="kaleido")


def makeTables(data):
    tables = []
    for i, country_name in enumerate(np.array(sorted(data.keys()))):
        try:
            to_data = data[country_name]['to']
            from_data = data[country_name]['from']
            title = F"""{country_name.capitalize()} exports {from_data['tot_tons']} tons per year <br>
{int(from_data['ocean_tons'])} ({from_data['ocean_perc']}%) end up on the ocean  <br>
{int(from_data['beach_tons'])} ({from_data['beach_perc']}%) end up on the beach <br>
"""
            dashPlotTable(country_name, to_data, from_data, title),
        except Exception as e:
            print(F"Failed for country: {country_name}: {traceback.print_exc()}")
    return tables

if __name__ == '__main__':
    tables = makeTables(data)

##

