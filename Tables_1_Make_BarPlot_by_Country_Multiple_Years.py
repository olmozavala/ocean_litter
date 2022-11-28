from os.path import join
import os
import json

import numpy as np
import shapely.speedups
import matplotlib.pyplot as plt
import collections
import pandas as pd

import subprocess
import shutil

# sftp://ozavala@enterprise/home/xbxu/hycom/GLBv0.08/nations
def remove_brackets(text):
    return text.replace('[','').replace(']','').replace('%','').replace(':','').strip()

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
            c_line = line
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

def jsonToCSV(json_object, file_name):
    print("Converting JSON to CSV")
    new_country = "Country Name, Tons Exported, Ends in the Ocean, Ends in the beach, \n"
    json_object = collections.OrderedDict(sorted(json_object.items()))
    csv_file = ""
    for country_name in json_object:
        country = json_object[country_name]

        try:
            country_txt = "\n" + new_country
            country_txt += F"{country_name.capitalize()}"
            # Adding the from countries
            from_data = []
            to_data = []
            if 'from' in country:
                country_txt += F", {country['from']['tot_tons']}, {country['from']['ocean_tons']}, {country['from']['beach_tons']} \n"
                if 'from' in country['from']:
                    for from_country in country['from']['from']:
                        from_data.append(F"Tons to {from_country['name']}, {from_country['tons']},")

            if 'to' in country:
                # Adding the to countries
                for to_country in country['to']['to']:
                    to_data.append(F"Tons from {to_country['name']}, {to_country['tons']},")

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

def getJsonByFolder(root_folder, all_files):
    not_found = []
    # Iterates over the countries in countries.json
    all_names = []
    json_object = {}
    for cur_file in all_files:
        if cur_file.find("swp") == -1:
            if cur_file.find("_from_") != -1:
                print(F"------ Reading file: {cur_file} --------")
                f = open(join(root_folder, cur_file), "r")
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
                f = open(join(root_folder, cur_file), "r")
                obj_to, country_name = readto(f)
                if obj_to == -1: # not found
                    if not(country_name in not_found):
                        not_found.append(country_name)

                if not(country_name in json_object.keys()):
                    json_object[country_name] = {}
                json_object[country_name]['to'] = obj_to

    return json_object

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


def makePNGs(root_folder, output_folder, plot_type="pie"):

    years_str = [x for x in os.listdir(root_folder) if not os.path.isfile(join(root_folder, x))]
    years_str.sort()
    num_years = len(years_str)
    # all_data contains all the countries data separated by year
    all_data = {}
    for c_year in years_str:
        file_names = os.listdir(join(root_folder, c_year))
        file_names.sort()

        with open(join(root_folder, c_year, "ReachedTablesData.json")) as f:
            data = json.load(f)

        # all_data[c_year] = getJsonByFolder(join(root_folder, c_year), file_names)
        all_data[c_year] = data

    # Here we assume all years have the same countries
    all_countries = all_data[years_str[0]].keys()
    # Iterate over all the countries

    for c_country in all_countries:
        print(F"Working with country: {c_country}...")
        country_from_data = {year:{} for year in years_str}
        country_to_data = {year:{} for year in years_str}

        # Iterate over all the years data for this country
        try:
            for id_year, c_year in enumerate(years_str):
                c_data = all_data[c_year][c_country]
                if 'from' in c_data.keys():
                    for c_from in c_data['from']['from']:
                        if c_from['name'] not in country_from_data[c_year]:
                            for y_str in years_str:
                                country_from_data[y_str][c_from['name']] = 0 # Initialize with zero for this country all years

                        country_from_data[c_year][c_from['name']] = c_from['perc']
                else:
                    country_from_data[c_year] = {}

            # Iterate over all the years data for this country
            for id_year, c_year in enumerate(years_str):
                c_data = all_data[c_year][c_country]
                if 'to' in c_data.keys():
                    for c_to in c_data['to']['to']:
                        if c_to['name'] not in country_to_data[c_year]:
                            for y_str in years_str:
                                country_to_data[y_str][c_to['name']] = 0 # Initialize with zero for this country all years

                        country_to_data[c_year][c_to['name']] = c_to['perc']
                else:
                    country_from_data[c_year] = {}
        except Exception as e:
            print(F"Failed for {c_country} e:{e}")
            continue

        ## -------------------------------------
        # ----- Making the plots -------------------
        fig, axs = plt.subplots(1,2, figsize=(15,5))

        # ----- From part -------------------
        if plot_type == 'pie':
            # Pie chart, where the slices will be ordered and plotted counter-clockwise:
            labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
            sizes = [15, 30, 45, 10]
            explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            plt.show()
        if plot_type == 'bar':
            if len(country_from_data[years_str[0]]) > 0:
                df = pd.DataFrame(country_from_data)
                df = df.sort_values(by=[years_str[0]],ascending=False)
                df = df.head(show_n_countries)
                # country_from_data has all the data for all the years. In each 'inside country' it has an array of values, one per year
                connected_countries = df.index
                tot_countries = len(connected_countries)
                df.plot.bar(ax=axs[0])
                axs[0].set_title(F"MPL from {c_country} to other countries by year (top {show_n_countries})")
                axs[0].set_ylabel("Percentage of MPL")
                axs[0].tick_params(labelrotation=30)

            # ----- To part -------------------
            if len(country_to_data[years_str[0]]) > 0:
                df = pd.DataFrame(country_to_data)
                df = df.sort_values(by=[years_str[0]],ascending=False)
                df = df.head(show_n_countries)
                # country_to_data has all the data for all the years. In each 'inside country' it has an array of values, one per year
                connected_countries = df.index
                tot_countries = len(connected_countries)
                df.plot.bar(ax=axs[1])
                axs[1].set_title(F"MPL towards {c_country} from other countries by year (top {show_n_countries})")
                axs[1].set_ylabel("Percentage of MPL")
                axs[1].tick_params(labelrotation=30)

        plt.tight_layout()
        plt.savefig(join(output_folder,F"{c_country}.png"))
        # plt.show()
        plt.close()

if __name__ == "__main__":
    # TODO First copy all the tables from bellow address to ./data/reached_data_tables inside this project
    # sftp://ozavala@enterprise/home/xbxu/hycom/GLBv0.08/nations
    shapely.speedups.enable()
    show_n_countries = 10

    root_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/reached_data_tables/Outputs"
    output_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/table_images/MultipleYears"

    makePNGs(root_folder, output_folder)

    # ---------------- Multiple years ---------------
    years = range(2017,2022)
    in_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/table_images/MultipleYears"
    pdf_output_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/reached_data_tables/Outputs"

    if not os.path.exists(pdf_output_folder):
        os.makedirs(pdf_output_folder)

    output_file = join(pdf_output_folder, F"ReachedTablesDataAll.pdf")
    makePDF(in_folder, output_file)