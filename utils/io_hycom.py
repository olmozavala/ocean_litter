import os
from os.path import join

def read_files(base_folder, years, wind=False):
    all_files = []
    for year in years:
        if wind:
            c_year_path = join(base_folder, F'{year}w')
        else:
            c_year_path = join(base_folder, F'{year}')
        files = os.listdir(c_year_path)
        for c_file in files:
            all_files.append(join(c_year_path, c_file))

    return all_files
