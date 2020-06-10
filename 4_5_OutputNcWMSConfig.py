from netCDF4 import Dataset
import numpy as np

if __name__ == "__main__":
    #  ------------ COAPS WEB  ------------------
    for i in range(1,13):
        try:
            # file_name_local = F"/home/data/UN_Litter_data/output/histo/Single_Release_FiveYears_EachMonth_2010_{i:02d}_histogram_one_eighth.nc"
            file_name_local = F"/data/UN_Litter_data/output/histo/Single_Release_FiveYears_EachMonth_2010_{i:02d}_histogram_one_eighth.nc"
            file_name = F"/Net/work/ozavala/WorldLitterOutput/histograms/Single_Release_FiveYears_EachMonth_2010_{i:02d}_histogram_one_eighth.nc"
            ds = Dataset(file_name_local, "r", format="NETCDF4")
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
    # all_max = []
    # for i in range(3,13):
    #     file_name = F"/home/data/UN_Litter_data/output/histo/Single_Release_FiveYears_EachMonth_2010_{i:02d}_histogram_one_eighth.nc"
    #     ds = Dataset(file_name, "r", format="NETCDF4")
    #     histo = ds['histo']
    #     max_val = int(np.nanmax(ds['histo']))
    #     all_max.append(max_val)
    #     var = F"""        <dataset id="histo_{i:02d}" title="histo_{i:02d}" location="{file_name}" queryable="true" downloadable="true" dataReaderClass="" copyrightStatement="" moreInfo="" disabled="false" updateInterval="-1">
    #         <variables>
    #             <variable id="histo" title="histo{i:02d}" description="sea_surface_temperature" palette="x-Sst" belowMinColor="#FF000000" aboveMaxColor="#FF000000" noDataColor="transparent" numColorBands="250" disabled="false" colorScaleRange="1.0 {max_val}" scaling="logarithmic"/>
    #         </variables>
    #     </dataset>"""
    #     print(var)
    #
    # print(F"All max: {all_max}")

