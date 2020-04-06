import xarray as xr
from os.path import join
import numpy as np
import os

def all_to_rad(arr):
    return [np.deg2rad(x) for x in arr]

def combine_currents_winds(U_c, V_c, U_w, V_w, w_perc, rot_matrix):
    U_c, V_c, U_w, V_w = [x.values[0] for x in [U_c, V_c, U_w, V_w]]
    # =========== Rotating by an angle =========
    temp_wind_rot = np.dot(np.array([U_w.flatten(), V_w.flatten()]).T, rot_matrix)
    U_wnew = temp_wind_rot[:,0].reshape(U_w.shape)
    V_wnew = temp_wind_rot[:,1].reshape(V_w.shape)
    # xi = 2060
    # yi = 1406
    # print(F"Original {V_w[xi, yi]} {V_wnew[xi,yi]}")
    # =========== Reducing wind component ========
    U_c = U_c + U_wnew*w_perc
    V_c = V_c + V_wnew*w_perc
    return np.expand_dims(U_c, axis=0), np.expand_dims(V_c, axis=0)

def main():
    # Home
    # input_folder = "/home/data/UN_Litter_data/HYCOM"
    # output_folder = join(input_folder, "combined")
    # COAPS My PC
    # input_folder = "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/"
    # output_folder = "/data/COAPS_Net/work/ozavala/CurrentsAndWinds"
    # COAPS Compute nodes
    input_folder = "/nexsan/people/xbxu/hycom/GLBv0.08/"
    output_folder = "/Net/work/ozavala/CurrentsAndWinds"
    angle = np.deg2rad(.001)  # Switch to radians
    rot_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                           [np.sin(angle), np.cos(angle)]])
    w_perc = 3.5/100
    years = [2010]

    if not(os.path.exists(output_folder)):
        os.makedirs(output_folder)

    # Iterate over each year
    for year in years:
        # Obtain currents and winds files
        c_folder = join(input_folder, F"{year}")
        w_folder = join(input_folder, F"{year}w")
        c_files = os.listdir(c_folder)
        w_files = os.listdir(w_folder)
        c_files.sort()
        w_files.sort()
        for c_file in c_files:
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
                    u_comb, v_comb = combine_currents_winds(c_xr['surf_u'], c_xr['surf_v'],
                                                            w_xr['uwnd'], w_xr['vwnd'],
                                                            w_perc=w_perc, rot_matrix=rot_matrix)
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
                    ds.to_netcdf(join(output_folder, F"Combined_{c_file}"))
                else:
                    print(F"File not found: {c_file}")
            except Exception as e:
                print(F"Failed for: {c_file}")


if __name__ == "__main__":
    main()
