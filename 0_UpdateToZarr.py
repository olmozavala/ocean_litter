"""Convert trajectory NetCDF files to consolidated Zarr stores with xarray.

The main block processes every entry of its hard-coded HPC input directory.
Review those paths before running; importing this module does not convert files.
"""

from __future__ import annotations

from os import PathLike
from typing import Union


import xarray as xr
import os
from os.path import join

def convert_to_zarr(
    input_netcdf_file: Union[str, PathLike[str]],
    output_zarr_folder: Union[str, PathLike[str]],
) -> None:
    """Write a NetCDF dataset to a Zarr directory with consolidated metadata.

    Variables, coordinates, and attributes are passed through xarray. Opening
    with chunks={} requires Dask; writing requires a compatible Zarr backend.
    Destination handling follows xarray's default to_zarr mode; choose a new
    store unless you have checked the installed version's write behavior.
    """
    ds = xr.open_dataset(input_netcdf_file, chunks={})
    
    # Convert and save to Zarr format
    ds.to_zarr(output_zarr_folder, consolidated=True)

if __name__ == "__main__":
    input_folder = "/gpfs/home/osz09/scratch/output_final"
    output_folder = "/gpfs/home/osz09/scratch/output_final_zarr"
    # From all the files in input_folder run convert_to_zarr and save in output folder
    all_files = os.listdir(input_folder)
    for c_file in all_files:
        netcdf_file = join(input_folder, c_file)
        zarr_folder = join(output_folder, c_file.replace('.nc',''))
        print(f"Updating file: {c_file} to {zarr_folder}")
        convert_to_zarr(netcdf_file, zarr_folder)
