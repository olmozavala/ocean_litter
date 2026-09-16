"""Integration checks for the pinned unmarinelitter environment.

Run explicitly with that environment. All files are synthetic and temporary;
these tests require GCC for Parcels' JIT but no mounted HYCOM dataset or MPI.
"""

from datetime import timedelta
import importlib.util
import inspect
from pathlib import Path

import numpy as np
from parcels import ErrorCode, FieldSet, ParticleSet
import plotly.graph_objects as go
import xarray as xr

from mykernels.custom_particles import LitterParticle
from mykernels.wl_kernels import (
    AdvectionRK4Beached, BeachTesting_2D, BrownianMotion2DUnbeaching,
    UnBeaching, outOfBounds, periodicBC,
)
from utils.io_hycom import add_Kh, add_unbeaching_field


def test_legacy_parcels_netcdf_jit_and_restart(tmp_path):
    """Exercise the repository's chunking API, custom kernels, and file restart."""
    assert "field_chunksize" in inspect.signature(FieldSet.from_netcdf).parameters
    lat = np.linspace(20, 24, 8, dtype=np.float32)
    lon = np.linspace(-94, -90, 8, dtype=np.float32)
    shape = (3, len(lat), len(lon))
    forcing = tmp_path / "forcing.nc"
    xr.Dataset(
        {
            "surf_u": (("time", "lat", "lon"), np.full(shape, 0.1, dtype=np.float32)),
            "surf_v": (("time", "lat", "lon"), np.zeros(shape, dtype=np.float32)),
        },
        coords={
            "time": ("time", [0., 3600., 7200.], {"units": "seconds since 2010-01-01"}),
            "latitude": ("lat", lat), "longitude": ("lon", lon),
        },
    ).to_netcdf(forcing)
    auxiliary = tmp_path / "unbeaching.nc"
    xr.Dataset({
        name: (("lat", "lon"), np.zeros(shape[1:], dtype=np.float32))
        for name in ("unBeachU", "unBeachV")
    }).to_netcdf(auxiliary)
    fields = FieldSet.from_netcdf(
        [str(forcing)], {"U": "surf_u", "V": "surf_v"},
        {"lat": "latitude", "lon": "longitude", "time": "time"},
        allow_time_extrapolation=True, field_chunksize=(4, 4),
    )
    add_Kh(fields, lat, lon, 1.)
    add_unbeaching_field(fields, lat, lon, str(auxiliary))
    fields.add_constant("halo_west", lon[0])
    fields.add_constant("halo_east", lon[-1])
    fields.add_periodic_halo(zonal=True)
    particles = ParticleSet(fieldset=fields, pclass=LitterParticle, lon=[-92.], lat=[22.])
    kernels = particles.Kernel(AdvectionRK4Beached)
    kernels += particles.Kernel(BeachTesting_2D)
    kernels += particles.Kernel(UnBeaching)
    kernels += particles.Kernel(BrownianMotion2DUnbeaching)
    kernels += particles.Kernel(BeachTesting_2D)
    kernels += particles.Kernel(periodicBC)
    destination = tmp_path / "trajectory.nc"
    output = particles.ParticleFile(name=str(destination), outputdt=timedelta(seconds=60))
    particles.execute(
        kernels, runtime=timedelta(seconds=120), dt=timedelta(seconds=60),
        output_file=output, recovery={ErrorCode.ErrorOutOfBounds: outOfBounds},
        verbose_progress=False,
    )
    output.export()
    with xr.open_dataset(destination) as result:
        assert result.sizes["traj"] == 1
        assert result.sizes["obs"] >= 2
        assert {"lat", "lon", "time", "beached", "beached_count"} <= set(result.variables)
        assert np.isfinite(result.lon.values).all()
    restarted = ParticleSet.from_particlefile(
        fieldset=fields, pclass=LitterParticle, filename=str(destination), repeatdt=None,
    )
    assert restarted.size == 1
    assert np.isfinite(restarted[0].lon)


def test_zarr_conversion_and_plotly_image_export(tmp_path):
    """Check the storage and headless image-export backends used by scripts."""
    source = xr.Dataset({"value": ("obs", [1., 2., 3.])})
    store = tmp_path / "sample.zarr"
    source.to_zarr(store, consolidated=True)
    with xr.open_zarr(store, consolidated=True) as loaded:
        xr.testing.assert_equal(source, loaded)
    image = tmp_path / "table.png"
    go.Figure(go.Table(header={"values": ["Country"]}, cells={"values": [["Example"]]})).write_image(image)
    assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_local_dash_guide_endpoints():
    """Import the guide and serialize its layout, including clipboard controls."""
    path = Path(__file__).resolve().parents[1] / "0_Summary_Start_Here.py"
    spec = importlib.util.spec_from_file_location("local_guide_environment_test", path)
    guide = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guide)
    client = guide.app.server.test_client()
    for endpoint in ("/", "/_dash-layout", "/_dash-dependencies"):
        assert client.get(endpoint).status_code == 200
