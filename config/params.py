"""Enum keys for heterogeneous configuration dictionaries and data columns.

GlobalModel is the current name. Several legacy simulation modules still import
WorldLitter, which is not defined here; see Docs/CODE_GUIDE.md before running.
Enum values are identifiers, not physical quantities.
"""

from enum import Enum

class Preproc(Enum):
    """Configuration keys used when assigning release locations to GIS shapes."""
    shapes_folder = 1

class GlobalModel(Enum):
    """Keys for paths, filename sequences, dates, and simulation intervals.

    See the configuration table in Docs/CODE_GUIDE.md for expected value types
    and units. Keep numeric values stable because external code may store them.
    """
    years = 1
    base_folder = 2
    loc_folder = 3
    stats_folder = 20
    lat_files = 4
    lon_files = 5
    output_folder = 16
    output_file = 6
    wind_factor = 7
    repeat_release = 8
    output_freq = 9
    output_folder_web = 11
    countries_file = 12
    dt = 13
    unbeach_file = 15


class DataCols(Enum):
    """Column-name constants used by preprocessing and visualization data."""
    category = 'category'
    netcdf_file = 'file_name'
    cords_file = 'coords_file_name'
    center = 'location'
    time = 'time'
