"""Append newer trajectory observations to previously merged monthly releases.

The CLI takes YEAR MONTH and uses the paths/prefixes in the main block. Unlike
2_MergeRuns.py, this script retains every observation from both input files.
"""

from __future__ import annotations

from os import PathLike
from typing import Sequence, Union


from os.path import join
import xarray as xr
import sys
import os

def mergeFiles(
    prefix_prev: str,
    prefix_new: str,
    input_folder_1: Union[str, PathLike[str]],
    input_folder_2: Union[str, PathLike[str]],
    output_folder: Union[str, PathLike[str]],
    years: Sequence[int],
    months: Sequence[int],
) -> None:
    """Concatenate matching PREFIX_YEAR_MM.nc files along ``obs``.

    Each pair must describe the same release and compatible trajectory order.
    The output uses prefix_new. Boundary timestamps are not deduplicated, so
    inspect input overlap before calling. Existing destinations are deleted
    before reading inputs; use a distinct, already-created output directory.
    Failures are printed per year/month and processing continues.
    """

    assert output_folder != input_folder_1
    assert output_folder != input_folder_2

    for c_year in years:
        for c_month in months:
            try:
                print(F"Merging files for year {c_year} - {c_month}")

                output_file = join(output_folder, F"{prefix_new}_{c_year}_{c_month:02d}.nc")
                if os.path.exists(output_file):
                    print(F"Removing file {output_file} before writing...")
                    os.remove(output_file)

                f1 = join(input_folder_1,F"{prefix_prev}_{c_year}_{c_month:02d}.nc")
                f2 = join(input_folder_2,F"{prefix_new}_{c_year}_{c_month:02d}.nc")

                ds1 = xr.open_dataset(f1)
                ds2 = xr.open_dataset(f2)

                dmerged = xr.concat([ds1, ds2], dim='obs')
                    
                dmerged.to_netcdf(output_file)
                ds1.close()
                ds2.close()
                print("Done!")

            except Exception as e:
                print(F"Failed for {c_year}_{c_month}: {e}", flush=True)

if __name__ == "__main__":
    input_folder_1 = "/gpfs/home/osz09/scratch/output_final"
    input_folder_2 = "/gpfs/home/osz09/scratch/output_2022"
    output_folder =  "/gpfs/home/osz09/scratch/output_final_2022"
    prefix_prev = "TenYears_YesWinds_YesDiffusion_NoUnbeaching"
    prefix_new = "UpToDec2022_YesWinds_YesDiffusion_NoUnbeaching"

    # If running with bash
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    mergeFiles(prefix_prev, prefix_new, input_folder_1, input_folder_2, output_folder, [year], [month])

    # Running all at the same time
    #mergeFiles(prefix_prev, prefix_new, input_folder_1, input_folder_2, output_folder, range(2010,2021), range(1,13))
    # mergeFiles(prefix_prev, prefix_new, input_folder_1, input_folder_2, output_folder, range(2010,2022), range(1,13))

    