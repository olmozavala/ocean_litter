from os.path import join
import xarray as xr
import sys
import os

def mergeFiles(prefix, input_folder_1, input_folder_2, output_folder, years, months):
    """
    This code merges previous merged runs with new merged runs
    :param input_folder_1:
    :param input_folder_2:
    :param output_folder:
    :param years:
    :param months:

    :return:
    """

    assert output_folder != input_folder_1
    assert output_folder != input_folder_2

    for c_year in years:
        for c_month in months:
            try:
                print(F"Merging files for year {c_year} - {c_month}")

                output_file = join(output_folder, F"{prefix}_{c_year}_{c_month:02d}.nc")
                if os.path.exists(output_file):
                    print(F"Removing file {output_file} before writing..")
                    os.remove(output_file)

                f1 = join(input_folder_1,F"{prefix}_{c_year}_{c_month:02d}.nc")
                f2 = join(input_folder_2,F"{prefix}_{c_year}_{c_month:02d}_merged.nc")

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
    input_folder_1 = "/gpfs/home/osz09/scratch/PreviousData"
    input_folder_2 = "/gpfs/home/osz09/scratch/OutputsMerged"
    output_folder =  "/gpfs/home/osz09/scratch/Output_Final"
    file_prefix = "TenYears_YesWinds_YesDiffusion_NoUnbeaching"
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    #mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, range(2010,2021), range(1,13))
    #mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [year], [month])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2017], [5])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2010], [2])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2010], [3])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2010], [5])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2010], [7])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2010], [9])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2010], [11])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2011], [3])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2011], [5])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2012], [5])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2012], [7])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2012], [11])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2013], [1])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2013], [10])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2013], [12])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2014], [10])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2014], [12])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2015], [2])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2015], [4])
    mergeFiles(file_prefix, input_folder_1, input_folder_2, output_folder, [2017], [5])



