import pandas as pd
import geopandas as gpd
from os.path import join
import os
from enum import Enum
import json
from utils.ReplaceNames import replace_names
from config.MainConfig import get_op_config
from config.params import WorldLitter
import numpy as np
from shapely.geometry import Polygon, Point, MultiPoint
from config.MainConfig import get_preproc_config
from config.params import WorldLitter, Preproc
import shapely.speedups

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
    return text.replace('[','').replace(']','').replace(':','').strip()

def readto(f, json_names, json_ids):
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

def readfrom(f, json_names, json_ids):
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

if __name__ == "__main__":
    # config = get_preproc_config()
    #
    # input_folder = config[Preproc.shapes_folder]
    # output_file = config[WorldLitter.countries_file]
    # file_countries = 'ne_50m_admin_0_countries.shp'
    # release_loc_folder = config[WorldLitter.loc_folder]
    # lat_files = config[WorldLitter.lat_files]
    # lon_files = config[WorldLitter.lon_files]
    # geo_countries = gpd.GeoDataFrame.from_file(input_folder+file_countries)
    # print(geo_countries['ADMIN'])

    config = get_op_config()

    input_folder = config[WorldLitter.stats_folder]
    output_folder = config[WorldLitter.output_folder_web]
    all_files = os.listdir(input_folder)
    shapely.speedups.enable()
    json_countries_file = join(output_folder,'countries.json')

    not_found = []
    with open(json_countries_file) as f:
        data = json.load(f)
        all_json_names = [x['properties']['name'] for x in data['features']]
        all_ids = [x['properties']['id'] for x in data['features']]

        # for i, name in enumerate(all_json_names):
        #     if name.lower().find("congo") != -1:
        #         print(F"{name} id: {all_ids[i]}")

        all_names = []
        json_object = {}
        for cur_file in all_files:
            # for cur_file in ["sum_from_ISR.txt"]:
            if cur_file.find("swp") == -1:
                if cur_file.find("_from_") != -1:
                    print(F"------ Reading file: {cur_file} --------")
                    f = open(join(input_folder, cur_file), "r")
                    obj_from, country_name = readfrom(f, all_json_names, all_ids)
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
                    f = open(join(input_folder, cur_file), "r")
                    obj_from, country_name = readto(f, all_json_names, all_ids)
                    if obj_from == -1: # not found
                        if not(country_name in not_found):
                            not_found.append(country_name)

                    if not(country_name in json_object.keys()):
                        json_object[country_name] = {}
                    json_object[country_name]['to'] = obj_from

        json_txt = json.dumps(json_object)
        output_file = join(output_folder,'ReachedTablesData.json')
        f = open(output_file, "w+")
        f.write(json_txt)

        not_found.sort()
        print(not_found)
