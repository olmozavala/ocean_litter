import os
from os.path import join
from datetime import date

def read_files(base_folder, years, wind=False, start_date=0):
    all_files = []
    for year in years:
        if wind:
            c_year_path = join(base_folder, F'{year}w')
        else:
            c_year_path = join(base_folder, F'{year}c')
        files = os.listdir(c_year_path)
        # Filtering just dates after initial date
        if start_date == 0:
            final_files = files
        else:
            final_files = []
            ds = [x.split('_')[3] for x in files]
            all_dates = [date(int(x[0:4]), int(x[4:6]), int(x[6:8])) for x in ds]
            for i, c_date in enumerate(all_dates):
                if c_date >= start_date:
                    final_files.append(files[i])

        for c_file in final_files:
            all_files.append(join(c_year_path, c_file))

    all_files.sort()
    return all_files

def read_files_combined(base_folder, years):
    all_files = []
    for year in years:
        c_year_path = join(base_folder, F'{year}')
        files = os.listdir(c_year_path)
        for c_file in files:
            all_files.append(join(c_year_path, c_file))

    all_files.sort()
    return all_files
