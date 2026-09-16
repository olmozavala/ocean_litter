"""Locate yearly HYCOM forcing and attach auxiliary fields to a Parcels FieldSet.

These helpers use the legacy Parcels API used by models/models.py.
"""

from __future__ import annotations

from os import PathLike
from typing import TYPE_CHECKING, Iterable, List, Union

if TYPE_CHECKING:
    from parcels import FieldSet
    from numpy.typing import ArrayLike


from parcels import Field
import os
from netCDF4 import Dataset
from os.path import join
from datetime import datetime
import numpy as np

def read_files(
    base_folder: Union[str, PathLike[str]],
    years: Iterable[int],
    wind: bool = False,
    start_date: Union[datetime, int] = 0,
    end_date: Union[datetime, int] = 0,
) -> List[str]:
    """Return sorted paths from YEAR folders, or YEARc when ``wind=True``.

    YEARc already includes currents plus 1% wind; this function does not mix
    fields. Missing year directories are skipped. With ``start_date=0``, all
    directory entries are returned and ``end_date`` is ignored. Otherwise the
    fifth underscore-separated filename token must begin with YYYYMMDD.
    Dates are parsed at midnight and compared inclusively; nonzero start hours
    therefore exclude that day's midnight. ``end_date=0`` removes the upper
    bound. Entries are not filtered by extension, so use clean forcing folders.
    Malformed dated filenames can raise IndexError or ValueError.
    """
    all_files = []
    for year in years:
        # 2019 — ocean current
        # 2019w — wind filed
        # 2019c — ocean current+1% wind combined
        if wind:
            c_year_path = join(base_folder, F'{year}c')
        else:
            c_year_path = join(base_folder, F'{year}')

        if os.path.exists(c_year_path):
            files = os.listdir(c_year_path)
            # Filtering just dates after initial date
            if start_date == 0:
                final_files = files
            else:
                final_files = []
                # ds = [x.split('_')[3] for x in files]
                ds = [x.split('_')[4] for x in files]
                all_dates = [datetime(int(x[0:4]), int(x[4:6]), int(x[6:8]) ) for x in ds]
                for i, c_date in enumerate(all_dates):
                    if end_date != 0:
                        if start_date <= c_date <= end_date:
                            final_files.append(files[i])
                    else:
                        if c_date >= start_date:
                            final_files.append(files[i])

            for c_file in final_files:
                all_files.append(join(c_year_path, c_file))

    all_files.sort()
    return all_files

def add_unbeaching_field(
    field_set: FieldSet,
    lat: ArrayLike,
    lon: ArrayLike,
    input_file: Union[str, PathLike[str]],
) -> None:
    """Attach ``unBeachU`` and ``unBeachV`` to ``field_set`` in place.

    The NetCDF variables must be two-dimensional arrays matching the supplied
    latitude/longitude grid (degrees). Values are used as movement fields by
    UnBeaching with the existing spherical field conversions. The legacy reader
    opens the file in r+ mode, so it currently requires write access.
    """
    ds = Dataset(input_file, "r+", format="NETCDF4")

    unBeachU= Field('unBeachU', ds['unBeachU'][:,:],
                    lon=lon, lat=lat, allow_time_extrapolation=True,
                    fieldtype='Kh_meridional', mesh='spherical', field_chunksize=(2048,2048))
    unBeachV= Field('unBeachV', ds['unBeachV'][:,:],
                    lon=lon, lat=lat, allow_time_extrapolation=True,
                    fieldtype='Kh_zonal', mesh='spherical', field_chunksize=(2048,2048))

    field_set.add_field(unBeachU, 'unBeachU')
    field_set.add_field(unBeachV, 'unBeachV')

def add_Kh(field_set: FieldSet, lat: ArrayLike, lon: ArrayLike, kh: float) -> None:
    """Attach constant zonal and meridional diffusivity fields in place.

    ``lat`` and ``lon`` are one-dimensional coordinates in degrees. ``kh`` is
    the diffusivity in m²/s before Parcels' spherical field conversion. Both
    fields use float32 arrays with shape (len(lat), len(lon)).
    """
    kh_mer = Field('Kh_meridional', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                   lon=lon, lat=lat, allow_time_extrapolation=True,
                   fieldtype='Kh_meridional', mesh='spherical', field_chunksize=(2048,2048))
    kh_zonal = Field('Kh_zonal', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                     lon=lon, lat=lat, allow_time_extrapolation=True,
                     fieldtype='Kh_zonal', mesh='spherical', field_chunksize=(2048,2048))

    field_set.add_field(kh_mer, 'Kh_meridional')
    field_set.add_field(kh_zonal, 'Kh_zonal')
