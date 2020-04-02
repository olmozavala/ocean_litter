import pandas as pd
from os.path import join
import os
from enum import Enum
import json
from utils.ReplaceNames import replace_names

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

input_folder = '/home/olmozavala/Dropbox/COAPS/Work_Related/Dynamic_Animations_From_Positions/Reformat_Data/reached_data'
output_folder = '/home/olmozavala/Dropbox/COAPS/Work_Related/Dynamic_Animations_From_Positions/Reformat_Data/output/reached_json'

all_files = os.listdir(input_folder)

json_object = {}
for cur_file in all_files:
    if(cur_file.find(".csv") != -1):
        print(F"------ Reading file: {cur_file} --------")
        cur_country = replace_names(cur_file.replace(".csv",""))
        # data_csv = np.loadtxt(join(input_folder, cur_file), dtype=np.str, delimiter=',')
        data_csv = pd.read_csv(join(input_folder, cur_file), names=[C.AfricaName,C.AfricaParticles,C.AsiaName,C.AsiaParticles], index_col=False)

        # ------------- Iterate over the Africa names -------------
        data_africa = data_csv.loc[:,[C.AfricaName, C.AfricaParticles]].dropna()
        reached_africa = get_reached(data_africa, C.AfricaName, C.AfricaParticles)
        data_asia = data_csv.loc[:,[C.AsiaName, C.AsiaParticles]].dropna()
        reached_asia = get_reached(data_asia, C.AsiaName, C.AsiaParticles)

        json_object[cur_country] = {'Africa':reached_africa, 'Asia': reached_asia}

json_txt = json.dumps(json_object)
output_file = join(output_folder,'ReachedTablesData.json')
f = open(output_file, "w+")
f.write(json_txt)
