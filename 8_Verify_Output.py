from os.path import join
import os
import sys
import xarray as xr

if __name__ == "__main__":
    folder = "/data/COAPS_Net/work/ozavala/WorldLitterOutput/2010-2021_Twelve_Years"
    files = os.listdir(folder)
    files.sort()

    for c_file in files:
        try:
            ds = xr.open_dataset(join(folder, c_file))
            ds_vars = ds.variables
            ds.close()

        except Exception as e:
            print(F"Failed for {c_file}")

    print("Done!")
