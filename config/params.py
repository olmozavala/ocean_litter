from enum import Enum

class WorldLitter(Enum):
    years = 1
    base_folder = 2
    loc_folder = 3
    lat_files = 4
    lon_files = 5
    output_folder = 20
    output_file = 6
    wind_factor = 7
    repeat_release = 8
    output_freq = 9
    run_time = 10
    output_folder_web = 11
    countries_file = 12
    dt = 13


class DataCols(Enum):
    category = 'category'
    netcdf_file = 'file_name'
    cords_file = 'coords_file_name'
    center = 'location'
    time = 'time'
