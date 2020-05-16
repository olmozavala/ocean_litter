import pandas as pd
from os.path import join
import os
from enum import Enum
import json
from utils.ReplaceNames import replace_names
from config.MainConfig import get_op_config
from config.params import WorldLitter
import numpy as np

class C(Enum):
    AfricaName = 1
    AfricaParticles = 2
    AsiaName = 3
    AsiaParticles = 4

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

def readto(f):
    all_lines = f.readlines()
    country_name = remove_brackets(all_lines[0][33:-1]).lower()

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


def readfrom(f):
    all_lines = f.readlines()
    country_name = remove_brackets(all_lines[0][27:-1]).lower()
    tot_tons = int(all_lines[0][0:8])

    at_ocean = float(all_lines[1][0:8])
    at_ocean_perc = float(remove_brackets(all_lines[1][10:14]))

    at_beach = float(all_lines[2][0:8])
    at_beach_perc = float(all_lines[2][10:14])

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


if __name__ == "__main__":
    config = get_op_config()

    input_folder = config[WorldLitter.stats_folder]
    output_folder = config[WorldLitter.output_folder_web]
    all_files = os.listdir(input_folder)

    json_object = {}
    for cur_file in all_files:
        # for cur_file in ["sum_from_ISR.txt"]:
        if cur_file.find("swp") == -1:
            if cur_file.find("_from_") != -1:
                print(F"------ Reading file: {cur_file} --------")
                f = open(join(input_folder, cur_file), "r")
                obj_from, country_name = readfrom(f)

                if not(country_name in json_object.keys()):
                    json_object[country_name] = {}
                json_object[country_name]['from'] = obj_from

            if cur_file.find("_to_") != -1:
                print(F"------ Reading file: {cur_file} --------")
                f = open(join(input_folder, cur_file), "r")
                obj_from, country_name = readto(f)

                if not(country_name in json_object.keys()):
                    json_object[country_name] = {}
                json_object[country_name]['to'] = obj_from

    json_txt = json.dumps(json_object)
    output_file = join(output_folder,'ReachedTablesData.json')
    f = open(output_file, "w+")
    f.write(json_txt)
