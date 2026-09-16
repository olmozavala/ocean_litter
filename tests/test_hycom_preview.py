"""Numerical and input-handling checks for the local NetCDF viewer."""

from netCDF4 import Dataset
import numpy as np
import pytest

from utils.hycom_preview import EARTH_RADIUS, GULF_LATITUDE, GULF_LONGITUDE, discover_folders, field_figures, list_netcdf_files, load_preview, relative_vorticity


def test_solid_body_rotation_includes_spherical_metric():
    lat, lon = np.linspace(-80, 80, 801), np.arange(-180, 180, 2.)
    omega = 1e-5
    u = np.broadcast_to(omega * EARTH_RADIUS * np.cos(np.deg2rad(lat))[:, None],
                        (lat.size, lon.size)).copy()
    actual = relative_vorticity(u, np.zeros_like(u), lat, lon)
    expected = np.broadcast_to(2 * omega * np.sin(np.deg2rad(lat))[:, None], u.shape)
    np.testing.assert_allclose(actual[1:-1], expected[1:-1], atol=2e-10)


def test_periodic_longitude_derivative_and_missing_values():
    lat, lon = np.array([-20., 0., 20.]), np.arange(-180., 180.)
    v = np.broadcast_to(np.sin(np.deg2rad(lon))[None, :], (lat.size, lon.size)).copy()
    u = np.zeros_like(v)
    result = relative_vorticity(u, v, lat, lon)
    expected = np.cos(np.deg2rad(lon))[None, :] / (EARTH_RADIUS * np.cos(np.deg2rad(lat))[:, None])
    np.testing.assert_allclose(result, expected, atol=1e-11)
    u[1, 15] = np.nan
    assert np.isnan(relative_vorticity(u, v, lat, lon)[1, 15])
    pole_lat = np.array([0., 45., 90.])
    assert np.isnan(relative_vorticity(np.ones_like(v), v, pole_lat, lon)[-1]).all()


def test_year_discovery_and_file_filtering(tmp_path):
    for name in ['2010', '2010c', '2023w+', 'C2010_12', 'notes']:
        (tmp_path / name).mkdir()
    (tmp_path / '2022.nc').write_text('not a directory')
    assert discover_folders(tmp_path) == {'2010': ['2010', '2010c'], '2023': ['2023w+']}
    for name in ['b.nc', 'a.nc4', 'notes.txt']:
        (tmp_path / '2010' / name).touch()
    assert list_netcdf_files(tmp_path, '2010') == ['a.nc4', 'b.nc']
    with pytest.raises(ValueError):
        load_preview(tmp_path, '../2010', 'b.nc')
    with pytest.raises(ValueError):
        load_preview(tmp_path, '2010', '../b.nc')


def test_read_wind_first_record_and_crop_after_coordinate_reordering(tmp_path):
    directory = tmp_path / '2023w'
    directory.mkdir()
    path = directory / 'example.nc'
    with Dataset(path, 'w') as ds:
        ds.createDimension('time', 2)
        ds.createDimension('lat', 4)
        ds.createDimension('lon', 4)
        ds.createVariable('latitude', 'f8', ('lat',))[:] = [90, 60, 30, 0]
        ds.createVariable('longitude', 'f8', ('lon',))[:] = [0, 90, 180, 270]
        time = ds.createVariable('time', 'f8', ('time',))
        time.units = 'hours since 2000-01-01'
        time[:] = [0, 3]
        ds.createVariable('uwnd', 'f4', ('time', 'lon', 'lat'))[:] = 1
        ds.createVariable('vwnd', 'f4', ('time', 'lon', 'lat'))[:] = 0
    data = load_preview(tmp_path, '2023w', 'example.nc')
    np.testing.assert_array_equal(data['latitude'], [30])
    np.testing.assert_array_equal(data['longitude'], [-90])
    assert data['shape'] == (4, 4) and data['u'].shape == (1, 1)
    assert data['kind'] == 'Wind velocity' and data['records'] == 2
    assert data['time'] == '2000-01-01T00:00:00'
    for figure in field_figures(data, '2023w'):
        assert tuple(figure.layout.xaxis.range) == GULF_LONGITUDE
        assert tuple(figure.layout.yaxis.range) == GULF_LATITUDE
