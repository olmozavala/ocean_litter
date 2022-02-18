from os.path import join
import traceback
import json
from config.MainConfig import get_op_config
from config.params import GlobalModel
import plotly.graph_objs as go
import numpy as np
import plotly.graph_objects as go
import os
import subprocess
import shutil

MAX_ROWS = 15
config = get_op_config()
skip_countries = []
data = {}
global_year = 0


def addRows(data, data_type):
    add_others = False
    others_val = 0
    others_perc = 0
    rows = []
    dir_text = "to" if data_type == "from" else "from"
    for i in range(0, len(data[data_type])):
        c_row = data[data_type][i]
        if c_row['name'].lower() in skip_countries:
            continue

        if i > MAX_ROWS:
            others_val += int(c_row['tons'])
            others_perc += c_row['perc']
            add_others = True
        else:
            perc_txt = F"{c_row['perc']:0.1f}" if c_row['perc'] >= 0.1 else "less than 0.1"
            if c_row['tons'] > 1:
                rows.append(F"{formatNumbers(int(c_row['tons']))} {dir_text} {c_row['name']} ({perc_txt}%) ")
            else:
                if c_row['tons'] == 1:
                    rows.append(F"1 {dir_text} {c_row['name']} ({perc_txt}%) ")
                else:
                    rows.append(F"Less than 1 {dir_text} {c_row['name']} ({perc_txt}%) ")

    if add_others:
        if int(others_val) > 1:
            rows.append(F"{formatNumbers(others_val)} tons {dir_text} other countries ({others_perc:0.1f}%) ")
        else:
            if others_val == 1:
                rows.append(F"1 {dir_text} other countries ({others_perc:0.1f}%) ")
            else:
                rows.append(F"Less than 1 {dir_text} other countries ({others_perc:0.1f}%) ")

    return rows


def formatNumbers(number):
    return "{:,}".format(number)


def dashPlotTable(country_name,  to_data, from_data, title, output_folder):

    headerColor = '#E6E6E6'
    rowEvenColor = '#F8F8F8'
    rowOddColor = 'white'

    rows_from = addRows(from_data, 'from')
    rows_to = addRows(to_data, 'to')

    fig = go.Figure(data=[go.Table(header=dict(values=[F"Waste from {country_name.capitalize()} ({formatNumbers(from_data['tot_tons'])} tons)",
                                                       F"Waste towards {country_name.capitalize()} ({formatNumbers(to_data['tot_tons'])} tons)"],
                                               fill_color=headerColor,
                                               line_color='gray',
                                               height=25),
                                   cells=dict(values=[rows_from, rows_to],
                                              fill_color=[[rowEvenColor if i % 2 == 1 else rowOddColor for i in range(len(rows_from) + len(rows_to))]],
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
    fig.write_image(join(output_folder,F"{country_name.replace(' ','_')}.png"), scale=2, engine="kaleido")


def makeTables(data, output_folder):
    tables = []
    for i, country_name in enumerate(np.array(sorted(data.keys()))):
        # We have the option to remove some countries
        if country_name in skip_countries:
            continue

        try:
            to_data = {'name':country_name,'tot_tons':0,'to':[]}
            from_data = {'name':country_name,
                         'tot_tons':0,
                         'ocean_tons':0,
                         'ocean_perc':0,
                         'beach_tons':0,
                         'beach_perc':0,
                         'from':[]}
            if 'to' in data[country_name].keys():
                to_data = data[country_name]['to']
            if 'from' in data[country_name].keys():
                from_data = data[country_name]['from']

            title = F"""{country_name.capitalize()} exports approximately {formatNumbers(from_data['tot_tons'])} tons from 2010 to {global_year} <br>
{formatNumbers(int(from_data['ocean_tons']))} ({from_data['ocean_perc']}%) end up in the ocean  <br>
{formatNumbers(int(from_data['beach_tons']))} ({from_data['beach_perc']}%) end up in the beach <br>
"""
            dashPlotTable(country_name, to_data, from_data, title, output_folder),
        except Exception as e:
            # print(F"Failed for country: {country_name}:{i}: {traceback.print_exc()}")
            print(F"Failed for country: {country_name} Index:{i} e:{e}")
    return tables

def makePDF(input_folder, output_file):
    # Copy script
    print(F"Making pdf inside {input_folder}....")
    sh_file = "pngTopdf.sh"
    if not os.path.exists(join(input_folder, sh_file)):
        shutil.copyfile(sh_file, join(input_folder,sh_file))
    # Run it
    p = subprocess.Popen(["sh", join(input_folder,sh_file)], cwd=input_folder)
    p.wait()
    # Copy output file as output_folder
    shutil.copyfile(F"{join(input_folder,'ReachedTablesData.pdf')}", output_file)
    print(F"Saved to {output_file}")
    print("Done!")


if __name__ == '__main__':

    # input_file = join(config[GlobalModel.output_folder_web], 'ReachedTablesData.json')
    # print(F"Reading data from: {input_file}")
    # output_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/table_images/"
    # Reads all the data from the specified json file
    # with open(input_file) as f:
    #     data = json.load(f)
    # makeTables(data, output_folder)

    # ---------------- Multiple years ---------------
    years = range(2017,2022)
    in_folder= "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/reached_data_tables/Outputs"
    out_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/table_images/MultipleYears"
    pdf_output_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/reached_data_tables/Outputs/"

    for root_year in years: # I named it root_year because it create conflicts with other functions
        global_year = root_year
        input_file = join(in_folder, str(root_year), 'ReachedTablesData.json')
        print(F"Reading data from: {input_file}")
        output_folder = join(out_folder, str(root_year))

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(input_file) as f:
            data = json.load(f)

        makeTables(data, output_folder)
        output_file = join(pdf_output_folder, str(root_year), F"ReachedTablesData.pdf")
        makePDF(output_folder, output_file)
