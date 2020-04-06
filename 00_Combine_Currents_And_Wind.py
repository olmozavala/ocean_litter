import xarray as xr
from os.path import join
import numpy as np
import os
from multiprocessing import Pool

NUMBER_PROC = 2

def all_to_rad(arr):
    return [np.deg2rad(x) for x in arr]

def combine_currents_winds(U_c, V_c, U_w, V_w, LAT, w_perc, rot_matrix_nh, rot_matrix_sh):
    U_c, V_c, U_w, V_w = [x.values[0] for x in [U_c, V_c, U_w, V_w]]
    # =========== Rotating by an angle =========
    north_hem = LAT < 0
    south_hem = LAT >= 0
    U_flat = U_w.flatten()
    V_flat = V_w.flatten()
    temp_wind_rot = np.zeros((len(LAT),2))
    temp_wind_rot[north_hem,:] = np.dot(np.array([U_flat[north_hem], V_flat[north_hem]]).T, rot_matrix_nh)
    temp_wind_rot[south_hem,:] = np.dot(np.array([U_flat[south_hem], V_flat[south_hem]]).T, rot_matrix_sh)
    U_wnew = temp_wind_rot[:,0].reshape(U_w.shape)
    V_wnew = temp_wind_rot[:,1].reshape(V_w.shape)
    # xi = 2060
    # yi = 1406
    # print(F"Original {V_w[xi, yi]} {V_wnew[xi,yi]}")
    # =========== Reducing wind component ========
    U_c = U_c + U_wnew*w_perc
    V_c = V_c + V_wnew*w_perc
    return np.expand_dims(U_c, axis=0), np.expand_dims(V_c, axis=0)

def main(proc_number):
    # Home
    input_folder = "/home/data/UN_Litter_data/HYCOM"
    output_folder = join(input_folder, "combined")
    output_name = "Winds_25p_def_15deg"
    # COAPS My PC
    # input_folder = "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/"
    # output_folder = "/data/COAPS_Net/work/ozavala/CurrentsAndWinds"
    # COAPS Compute nodes
    # input_folder = "/nexsan/people/xbxu/hycom/GLBv0.08/"
    # output_folder = "/Net/work/ozavala/CurrentsAndWinds"
    deg = 15
    angle = np.deg2rad(deg)  # Switch to radians
    rot_matrix_nh = np.array([[np.cos(angle), -np.sin(angle)],
                           [np.sin(angle), np.cos(angle)]])
    angle = np.deg2rad(-deg)  # Switch to radians
    rot_matrix_sh = np.array([[np.cos(angle), -np.sin(angle)],
                              [np.sin(angle), np.cos(angle)]])

    w_perc = 2.5/100
    years = [2010]

    if not(os.path.exists(output_folder)):
        os.makedirs(output_folder)

    first_file = True
    # Iterate over each year
    for year in years:
        # Obtain currents and winds files
        c_folder = join(input_folder, F"{year}")
        w_folder = join(input_folder, F"{year}w")
        c_files = os.listdir(c_folder)
        w_files = os.listdir(w_folder)
        c_files.sort()
        w_files.sort()
        for ii, c_file in enumerate(c_files):
            if (ii % NUMBER_PROC) == proc_number:
                try:
                    date_str = c_file.split("_")[3][:-2]
                    hour_str = c_file.split("_")[4].split(".")[0]
                    found = False

                    for w_file in w_files:
                        if (w_file.find(F"{date_str}") != -1) and (w_file.find(F"{hour_str}") != -1):
                            corresponding_file = w_file
                            found = True
                            # TODO Remove c_file from list to make it faster
                            break

                    if found:
                        # Merge both files
                        print(F"{c_file}")
                        c_xr = xr.open_dataset(join(c_folder, c_file))
                        w_xr = xr.open_dataset(join(w_folder, w_file))
                        if first_file:
                            lat = c_xr['latitude']
                            lon = c_xr['longitude']
                            LAT = np.meshgrid(lon,lat)[1].flatten()
                            first_file = False

                        u_comb, v_comb = combine_currents_winds(c_xr['surf_u'], c_xr['surf_v'],
                                                                w_xr['uwnd'], w_xr['vwnd'],
                                                                LAT=LAT,
                                                                w_perc=w_perc,
                                                                rot_matrix_nh=rot_matrix_nh,
                                                                rot_matrix_sh = rot_matrix_sh)
                        ds = xr.Dataset(
                            {
                                "U_combined": (("time", "lat", "lon"), u_comb),
                                "V_combined": (("time", "lat", "lon"), v_comb),
                            },
                            {"time": c_xr['time'],
                             "lat": c_xr['lat'],
                             "lon": c_xr['lon'],
                             }
                        )
                        ds.to_netcdf(join(output_folder, F"{output_name}_{c_file}"))
                    else:
                        print(F"File not found: {c_file}")

                except Exception as e:
                    print(F"Failed for: {c_file}")


if __name__ == "__main__":
    p = Pool(NUMBER_PROC)
    p.map(main, range(NUMBER_PROC))
    print("Done!")