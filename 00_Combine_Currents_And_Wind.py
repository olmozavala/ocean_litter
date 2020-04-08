import xarray as xr
from os.path import join
import numpy as np
import os
from multiprocessing import Pool

NUMBER_PROC = 5

def all_to_rad(arr):
    return [np.deg2rad(x) for x in arr]

def combine_currents_winds(U_c, V_c, U_w, V_w, LAT, w_perc, rot_matrix_nh, rot_matrix_sh):
    """
    This function is in charge of combining currents and winds into a single field.
    The curreent U_combined = U + .025*winds*deflection
    :param U_c:
    :param V_c:
    :param U_w:
    :param V_w:
    :param LAT:
    :param w_perc:
    :param rot_matrix_nh:
    :param rot_matrix_sh:
    :return:
    """
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
    output_name = "Winds_25p_def_15deg"

    # -------- Home ---------------
    input_folder = "/home/data/UN_Litter_data/HYCOM"
    output_folder = join(input_folder, "combined")

    # -------------- COAPS My PC --------------
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
    years = np.arange(2010, 2011)

    first_file = True
    # Iterate over each year
    for year in years:
        c_output_folder = join(output_folder, F"{year}")
        if not(os.path.exists(c_output_folder)):
            os.makedirs(c_output_folder)

        # Obtain currents and winds files
        c_folder = join(input_folder, F"{year}")
        w_folder = join(input_folder, F"{year}w")
        c_files = os.listdir(c_folder)
        w_files = os.listdir(w_folder)
        c_files.sort()
        w_files.sort()
        output_folder_year = join(output_folder,F"{year}")
        if not(os.path.exists(output_folder_year)):
            os.makedirs(output_folder_year)
        for ii, c_file in enumerate(c_files):
            if (ii % NUMBER_PROC) == proc_number:
                # try:
                date_str = c_file.split("_")[3][:-2]
                month = date_str[4:6]
                print(month)
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
                    print(F"{c_file}", flush=True)
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

                    # For visualization purposes
                    # from img_viz.eoa_viz import EOAImageVisualizer
                    # mincbar = np.amin(u_comb)
                    # maxcbar = np.amax(u_comb)
                    # viz_obj = EOAImageVisualizer(disp_images=False, mincbar=mincbar, maxcbar=maxcbar)
                    # viz_obj.plot_3d_data_np([c_xr['surf_u'], w_xr['uwnd'], u_comb],
                    #                         var_names=['U_original', 'U_wind', 'U_combined'],
                    #                         z_levels=[0], title=F'U',
                    #                         file_name_prefix=F'U_{c_file}',
                    #                         flip_data=True)
                    #
                    # viz_obj.plot_3d_data_np([c_xr['surf_v'], w_xr['vwnd'], v_comb],
                    #                         var_names=['V_original', 'V_wind', 'V_combined'],
                    #                         file_name_prefix=F'V_{c_file}',
                    #                         z_levels=[0], title=F'V', flip_data=True)

                    ds = xr.Dataset(
                        {
                            "U_combined": (("time", "lat", "lon"), u_comb),
                            "V_combined": (("time", "lat", "lon"), v_comb),
                        },
                        {"time": c_xr['time'],
                         "lat": lat,
                         "lon": lon,
                         }
                    )
                    ds.to_netcdf(join(output_folder_year, F"{output_name}_{c_file}"))
                else:
                    print(F"File not found: {c_file}")

                # except Exception as e:
                #     print(F"Failed for: {c_file} error: {e}")


if __name__ == "__main__":
    p = Pool(NUMBER_PROC)
    p.map(main, range(NUMBER_PROC))
    print("Done!")

