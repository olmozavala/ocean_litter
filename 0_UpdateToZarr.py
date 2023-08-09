import xarray as xr
import os
from os.path import join

def convert_to_zarr(input_netcdf_file, output_zarr_folder):
    # Open the netCDF file using xarray
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
