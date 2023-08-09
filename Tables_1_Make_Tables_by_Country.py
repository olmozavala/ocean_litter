import pandas as pd
import geopandas as gpd
from os.path import join
import os
from enum import Enum
import json
from utils.several_utils import replace_names
from config.MainConfig import get_op_config
from config.params import WorldLitter
import numpy as np
from shapely.geometry import Polygon, Point, MultiPoint
from config.MainConfig import get_preproc_config
from config.params import WorldLitter, Preproc
import shapely.speedups
import matplotlib.pyplot as plt
import collections

# sftp://ozavala@enterprise/home/xbxu/hycom/GLBv0.08/nations
def get_reached(data, col_name, col_particle):
    reached = {}
    for c_reached_country in data[col_name].values:
        country_data = data[data[col_name] == c_reached_country]
        numb_str = country_data[col_particle].values[0]
        arrived = int((numb_str.split('[')[0]).replace(',', ''))
        total = int((numb_str.split('[')[1]).replace(']', '').replace(',', ''))
        reached[replace_names(c_reached_country)] = [arrived, total]
    return reached

def remove_brackets(text):
    return text.replace('[','').replace(']','').replace('%','').replace(':','').strip()

def readto_nodecay(f, json_names, json_ids):
    all_lines = f.readlines()

    table_country_name = remove_brackets(all_lines[0][30:-1]).lower()
    country_id = remove_brackets(all_lines[0][30:34])
    try:
        country_name = json_names[json_ids.index(country_id)].lower()

        tot_tons = int(all_lines[0][0:8])
        data_to = []
        for c_line in all_lines[2:]:
            tons = float(c_line[0:8])
            perc = float(c_line[10:14])
            name = remove_brackets(c_line[21:-1])
            tobj = {
                'name': name,
                'tons': tons,
                'perc': perc
            }
            data_to.append(tobj)

        obj_to = {
            'name': country_name,
            'tot_tons': tot_tons,
            'to': data_to
        }
        return obj_to, country_name
    except Exception as e:
        print(F"Not found: {table_country_name}")
        return -1, table_country_name

def readfrom_nodecay(f, json_names, json_ids):
    """
    Reads a single file with the statistics and matches the name with the json names being used
    :param f:
    :param json_names:
    :return:
    """
    all_lines = f.readlines()

    table_country_name = remove_brackets(all_lines[0][30:-1]).lower()
    country_id = remove_brackets(all_lines[0][25:30])
    tot_tons = int(all_lines[0][0:8])

    at_ocean = float(all_lines[1][0:8])
    at_ocean_perc = float(remove_brackets(all_lines[1][10:14]))

    at_beach = float(all_lines[2][0:8])
    at_beach_perc = float(all_lines[2][10:14])

    try:
        country_name = json_names[json_ids.index(country_id)].lower()

        data_from = []
        for c_line in all_lines[4:]:
            tons = float(c_line[0:8])
            perc = float(c_line[10:14])
            name = remove_brackets(c_line[21:-1])
            tobj = {
                'name': name,
                'tons': tons,
                'perc': perc
            }
            data_from.append(tobj)

        obj_from = {
            'name': country_name,
            'tot_tons': tot_tons,
            'ocean_tons': at_ocean,
            'ocean_perc': at_ocean_perc,
            'beach_tons': at_beach,
            'beach_perc': at_beach_perc,
            'from': data_from
        }
        return obj_from, country_name
    except Exception as e:
        print(F"Not found: {table_country_name}")
        return -1, table_country_name

def readto(f):
    all_lines = f.readlines()

    first_line = all_lines[0].split(';')
    table_country_name = remove_brackets(first_line[6]).lower()
    country_id = remove_brackets(first_line[5])
    try:
        country_name = all_lines[0].split('[')[1].split(']')[0]

        tot_tons = int(first_line[0])
        data_to = []
        for line in all_lines[2:]:
            c_line = line.split(';')
            tons = float(c_line[0])
            perc = float(remove_brackets(c_line[1]))
            name = remove_brackets(c_line[3])
            tobj = {
                'name': name,
                'tons': tons,
                'perc': perc
            }
            data_to.append(tobj)

        obj_to = {
            'name': country_name,
            'tot_tons': tot_tons,
            'to': data_to
        }
        return obj_to, country_name
    except Exception as e:
        print(F"Not found: {table_country_name}")
        return -1, table_country_name

def readfrom(f):
    """
    Reads a single file with the statistics and matches the name with the json names being used
    :param f:
    :param json_names:
    :return:
    """
    all_lines = f.readlines()

    first_line = all_lines[0].split(';')
    table_country_name = remove_brackets(first_line[4]).lower()
    country_id = remove_brackets(first_line[3])
    tot_tons = int(first_line[0])

    at_ocean = float(all_lines[1].split(';')[0])
    at_ocean_perc = float(remove_brackets(all_lines[1].split(';')[1]))

    at_beach = float(all_lines[2].split(';')[0])
    at_beach_perc = float(remove_brackets(all_lines[2].split(';')[1]))

    try:
        country_name = all_lines[0].split('[')[1].split(']')[0]

        data_from = []
        for line in all_lines[4:]:
            # c_line = line.split(';')
            # tons = float(c_line[0])
            # perc = float(c_line[1])
            # name = remove_brackets(c_line[3])

            # c_line = line
            # tons = float(c_line[0:8])
            # perc = float(c_line[10:14])
            # name = remove_brackets(c_line[21:-1])

            c_line = line.split(";")
            tons = float(c_line[0])
            perc = float(remove_brackets(c_line[1]))
            name = remove_brackets(c_line[3])

            tobj = {
                'name': name,
                'tons': tons,
                'perc': perc
            }
            data_from.append(tobj)

        obj_from = {
            'name': country_name,
            'tot_tons': tot_tons,
            'ocean_tons': at_ocean,
            'ocean_perc': at_ocean_perc,
            'beach_tons': at_beach,
            'beach_perc': at_beach_perc,
            'from': data_from
        }
        return obj_from, country_name
    except Exception as e:
        print(F"Not found: {table_country_name} Exception: {e}")
        return -1, table_country_name

def jsonToCSV(json_object, file_name):
    print("Converting JSON to CSV")
    json_object = collections.OrderedDict(sorted(json_object.items()))
    header_line = "Country Name, Tons Exported, Ends in the Ocean, Ends in the beach"
    csv_file = ""
    for country_name in json_object:
        country = json_object[country_name]

        try:
            country_txt = F"\n {header_line},Waste from {country_name.capitalize()},, Waste towards {country_name.capitalize()} \n"
            country_txt += F"{country_name.capitalize()}"
            # Adding the from countries
            from_data = []
            to_data = []
            if 'from' in country:
                country_txt += F", {country['from']['tot_tons']}, {country['from']['ocean_tons']}, {country['from']['beach_tons']} \n"
                if 'from' in country['from']:
                    for from_country in country['from']['from']:
                        from_data.append(F"To {from_country['name']}, {from_country['tons']},")

            if 'to' in country:
                # Adding the to countries
                for to_country in country['to']['to']:
                    to_data.append(F"From {to_country['name']}, {to_country['tons']},")

            rows = max(len(from_data), len(to_data))
            for i in range(rows):
                c_row = ",,,,"
                if i < len(from_data):
                    c_row += from_data[i]
                else:
                    c_row += ",,"

                if i < len(to_data):
                    c_row += to_data[i]

                country_txt += c_row + "\n"

            csv_file += country_txt

        except Exception as e:
            print(F"Failed for {country_name}: {e}")

    f = open(file_name, 'w')
    f.write(csv_file)

    print("Done!")

def makeJsonAndCsvFiles(stats_folder, output_folder):

    all_files = os.listdir(stats_folder)
    all_files.sort()
    shapely.speedups.enable()

    not_found = []
    # Iterates over the countries in countries.json
    all_names = []
    json_object = {}
    for cur_file in all_files:
        if cur_file.find("swp") == -1:
            if cur_file.find("_from_") != -1:
                print(F"------ Reading file: {cur_file} --------")
                f = open(join(stats_folder, cur_file), "r")
                obj_from, country_name = readfrom(f)
                if obj_from == -1: # not found
                    if not(country_name in not_found):
                        not_found.append(country_name)

                if not(country_name in json_object.keys()):
                    json_object[country_name] = {}
                json_object[country_name]['from'] = obj_from
                if not(country_name in all_names):
                    # Comment this part, only for debuggin
                    all_names.append(country_name)

            if cur_file.find("_to_") != -1:
                print(F"------ Reading file: {cur_file} --------")
                f = open(join(stats_folder, cur_file), "r")
                obj_to, country_name = readto(f)
                if obj_to == -1: # not found
                    if not(country_name in not_found):
                        not_found.append(country_name)

                if not(country_name in json_object.keys()):
                    json_object[country_name] = {}
                json_object[country_name]['to'] = obj_to

    # Eliminating countries that do not have from and to
    keys = list(json_object.keys())
    for key in keys:
        if 'from' not in json_object[key]:
            del json_object[key]

    json_txt = json.dumps(dict(sorted(json_object.items())))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file = join(output_folder, 'ReachedTablesData.json')
    output_file_csv = join(output_folder, 'ReachedTablesData.csv')
    jsonToCSV(json_object, output_file_csv)
    f = open(output_file, "w+")
    f.write(json_txt)

    not_found.sort()
    print(F"Saved at: {output_folder}")
    print(F"It failed for a total of {len(not_found)}:\n {not_found}")


if __name__ == "__main__":
    # TODO First copy all the tables from bellow address to ./data/reached_data_tables inside this project
    # sftp://ozavala@enterprise/home/xbxu/hycom/GLBv0.08/nations
    config = get_op_config()

    # input_folder= config[WorldLitter.stats_folder]
    # output_folder = config[WorldLitter.output_folder]
    # makeJsonAndCsvFiles(input_folder, output_folder)
    # ----------------- Multiple years ---------------
    years = range(2017,2022)
    rfolder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/reached_data_tables/MultipleYears"
    ofolder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/reached_data_tables/Outputs"
    for year in years:
        input_folder = join(rfolder, F"C{year}_12")
        output_folder = join(ofolder, F"{year}")
        makeJsonAndCsvFiles(input_folder, output_folder)