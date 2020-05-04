from enum import Enum

class Preproc(Enum):
    shapes_folder = 1

class WorldLitter(Enum):
    years = 1
    base_folder = 2
    loc_folder = 3
    lat_files = 4
    lon_files = 5
    output_folder = 16
    output_file = 6
    wind_factor = 7
    repeat_release = 8
    output_freq = 9
    end_date = 10
    output_folder_web = 11
    countries_file = 12
    dt = 13
    start_date = 14
    unbeach_file = 15


class DataCols(Enum):
    category = 'category'
    netcdf_file = 'file_name'
    cords_file = 'coords_file_name'
    center = 'location'
    time = 'time'
