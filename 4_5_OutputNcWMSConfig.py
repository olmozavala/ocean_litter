from netCDF4 import Dataset
import numpy as np

if __name__ == "__main__":
    #  ------------ COAPS WEB  ------------------
    for i in range(1,13):
        try:
            # file_name_local = F"/home/data/UN_Litter_data/output/histo/Single_Release_FiveYears_EachMonth_2010_{i:02d}_2020-04-19_21_18_output_histogram_one_quarter.nc"
            file_name = F"/data/COAPS_Net/work/ozavala/WorldLitterOutput/histograms/Single_Release_FiveYears_EachMonth_2010_{i:02d}_histogram_one_quarter.nc"
            ds = Dataset(file_name, "r", format="NETCDF4")
            histo = ds['histo']
            max_val = np.nanmax(ds['histo'])
            var = F"""        <dataset id="histo_{i:02d}" title="histo_{i:02d}" location="{file_name}" queryable="true" downloadable="true" dataReaderClass="" copyrightStatement="" moreInfo="" disabled="false" updateInterval="-1">
                <variables>
                    <variable id="histo" title="histo{i:02d}" description="sea_surface_temperature" palette="x-Sst" belowMinColor="#FF000000" aboveMaxColor="#FF000000" noDataColor="transparent" numColorBands="250" disabled="false" colorScaleRange="1.0 {max_val}" scaling="logarithmic"/>
                </variables>
            </dataset>"""
            print(var)
        except Exception as e:
            print(F"Failed for {file_name_local}")


    #  -------------------- Hom-------------------- e
    # for i in range(8,13):
    #     file_name = F"/home/data/UN_Litter_data/output/histo/Single_Release_FiveYears_EachMonth_2010_{i:02d}_2020-04-19_21_18_output_histogram_one_quarter.nc"
    #     ds = Dataset(file_name, "r", format="NETCDF4")
    #     histo = ds['histo']
    #     max_val = np.nanmax(ds['histo'])
    #     var = F"""        <dataset id="histo_{i:02d}" title="histo_{i:02d}" location="{file_name}" queryable="true" downloadable="true" dataReaderClass="" copyrightStatement="" moreInfo="" disabled="false" updateInterval="-1">
    #         <variables>
    #             <variable id="histo" title="histo{i:02d}" description="sea_surface_temperature" palette="x-Sst" belowMinColor="#FF000000" aboveMaxColor="#FF000000" noDataColor="transparent" numColorBands="250" disabled="false" colorScaleRange="1.0 {max_val}" scaling="logarithmic"/>
    #         </variables>
    #     </dataset>"""
    #     print(var)

