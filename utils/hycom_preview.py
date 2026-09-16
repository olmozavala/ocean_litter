"""Read HYCOM surface fields and prepare bounded-size interactive previews.

Relative vertical vorticity on a sphere (east/north velocity components):
    zeta = [dv/dlambda - d(u cos(phi))/dphi] / (R cos(phi))
Angles are radians, R is metres, and the result is s^-1. Derivatives are
computed on the native grid before thinning for display. No Coriolis term
is added. The singular pole and missing-data derivative stencils are masked.
"""

from __future__ import annotations

from functools import lru_cache
from os import PathLike
from pathlib import Path
import re
import threading
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

from netCDF4 import Dataset, Variable, num2date
import numpy as np
from numpy.typing import ArrayLike, NDArray
import plotly.graph_objects as go


PathInput = Union[str, PathLike[str]]
FloatArray = NDArray[np.floating[Any]]
FolderCatalog = Dict[str, List[str]]


class PreviewData(TypedDict):
    """One cropped, optionally thinned surface record for both plots.

    Coordinates are 1-D degrees; u/v and vorticity are (latitude, longitude)
    arrays in m/s and s^-1, respectively. NaN represents missing values.
    ``shape`` describes the full native grid; ``stride`` applies only to the
    display crop. ``records`` is the source time count, although only record
    zero is read. Cached arrays are shared: callers must treat them as read-only.
    """

    latitude: FloatArray
    longitude: FloatArray
    u: FloatArray
    v: FloatArray
    vorticity: FloatArray
    shape: Tuple[int, int]
    stride: int
    time: str
    records: int
    kind: str


EARTH_RADIUS = 6_371_000.0
YEAR_FOLDER = re.compile(r"^(?:19|20)\d{2}.*$")
NETCDF_LOCK = threading.Lock()  # The netCDF C library is not thread-safe.
MAX_PREVIEW_SIDE = 650
GULF_LONGITUDE = (-99.0, -79.0)
GULF_LATITUDE = (18.0, 32.0)


def discover_folders(root: PathInput) -> FolderCatalog:
    """Group sorted directories beginning with a year from 1900–2099.

    Return year strings mapped to full folder names, including forcing suffixes.
    Files are ignored. Missing/unreadable roots propagate filesystem errors.
    """
    catalog = {}
    for path in sorted(Path(root).iterdir()):
        if YEAR_FOLDER.fullmatch(path.name) and path.is_dir():
            catalog.setdefault(path.name[:4], []).append(path.name)
    return catalog


def checked_folder(root: PathInput, folder: Optional[str]) -> Path:
    """Validate a year-prefixed basename and join it to the supplied root.

    Reject empty values and path components; existence is checked by callers.
    Symlinks are not resolved, so this is not a filesystem confinement boundary.
    """
    if not folder or not YEAR_FOLDER.fullmatch(folder) or Path(folder).name != folder:
        raise ValueError("Choose a valid year folder.")
    return Path(root) / folder


def list_netcdf_files(root: PathInput, folder: str) -> List[str]:
    """List .nc, .nc4, and .cdf basenames in lexical navigation order.

    Extension matching ignores case; no recursive search or content inspection
    is performed. Invalid folder names raise ValueError; I/O errors propagate.
    """
    return sorted(p.name for p in checked_folder(root, folder).iterdir()
                  if p.suffix.lower() in {".nc", ".nc4", ".cdf"} and p.is_file())


def relative_vorticity(
    u: FloatArray, v: FloatArray, latitude: ArrayLike, longitude: ArrayLike,
) -> FloatArray:
    """Return relative vertical vorticity in s^-1 on the input grid.

    u/v are eastward/northward velocities in m/s, shaped (latitude, longitude).
    Coordinates are degrees, strictly increasing after longitude unwrapping,
    with at least three points per axis; violations raise ValueError. Nonuniform
    spacing is supported. A complete, nonduplicated longitude cycle uses centered
    seam derivatives; other boundaries use second-order one-sided differences.
    Poles, missing centers, and affected derivative stencils become NaN. Inputs
    are not modified. No planetary vorticity term is added.
    """
    phi = np.deg2rad(np.asarray(latitude, dtype=np.float64))
    lam = np.unwrap(np.deg2rad(np.asarray(longitude, dtype=np.float64)))
    if phi.ndim != 1 or lam.ndim != 1 or min(phi.size, lam.size) < 3:
        raise ValueError("Vorticity requires at least three 1-D latitude/longitude points.")
    if u.shape != (phi.size, lam.size) or v.shape != u.shape:
        raise ValueError("Velocity dimensions do not match latitude and longitude.")
    if not np.all(np.diff(phi) > 0) or not np.all(np.diff(lam) > 0):
        raise ValueError("Latitude and longitude must be strictly increasing.")
    cos_phi = np.cos(phi)[:, None].astype(np.result_type(u.dtype, np.float32))
    dvdlam = np.gradient(v, lam, axis=1, edge_order=2)
    # A complete, nonduplicated longitude cycle gets centered seam derivatives.
    step = np.median(np.diff(lam))
    if abs(lam[-1] - lam[0] + step - 2 * np.pi) < step * .1:
        dvdlam[:, 0] = np.gradient(
            v[:, [-1, 0, 1]], [lam[-1] - 2*np.pi, lam[0], lam[1]],
            axis=1, edge_order=2,
        )[:, 1]
        dvdlam[:, -1] = np.gradient(
            v[:, [-2, -1, 0]], [lam[-2], lam[-1], lam[0] + 2*np.pi],
            axis=1, edge_order=2,
        )[:, 1]
    with np.errstate(invalid="ignore", divide="ignore"):
        curl = (dvdlam - np.gradient(u * cos_phi, phi, axis=0, edge_order=2))
        curl /= EARTH_RADIUS * cos_phi
    curl[np.abs(cos_phi[:, 0]) < 1e-6, :] = np.nan
    # A missing center must stay missing even if its neighbor stencil is valid.
    curl[~np.isfinite(u) | ~np.isfinite(v)] = np.nan
    return curl


def _read_surface(variable: Variable, lat_dim: str, lon_dim: str) -> NDArray[np.float32]:
    """Read index zero on nonspatial dimensions, returning (lat, lon) float32.

    Masked values become NaN; transposed spatial axes are normalized. Unsupported
    dimension layouts raise ValueError. Coordinate names come from the dataset.
    """
    index = tuple(slice(None) if d in {lat_dim, lon_dim} else 0
                  for d in variable.dimensions)
    data = np.ma.asarray(variable[index], dtype=np.float32).filled(np.nan)
    dims = [d for d in variable.dimensions if d in {lat_dim, lon_dim}]
    if dims == [lon_dim, lat_dim]:
        data = data.T
    elif dims != [lat_dim, lon_dim]:
        raise ValueError(f"Unsupported dimensions for {variable.name}: {variable.dimensions}")
    return data


@lru_cache(maxsize=3)
def _load_preview(path: str, modified_ns: int, file_size: int) -> PreviewData:
    """Read one record under the NetCDF lock and cache only the display crop.

    modified_ns and file_size participate in the cache key, invalidating entries
    when file metadata changes. Prefer surf_u/surf_v, falling back to uwnd/vwnd;
    coordinates must be rectilinear. Normalize axes, compute native-grid curl,
    then crop to Gulf bounds and thin to MAX_PREVIEW_SIDE. The three-entry cache
    returns shared arrays and metadata; callers must not mutate them.
    """
    # Cache only thinned fields, keyed by file identity and modification time.
    with NETCDF_LOCK, Dataset(path) as ds:
        lat_var, lon_var = ds["latitude"], ds["longitude"]
        if lat_var.ndim != 1 or lon_var.ndim != 1:
            raise ValueError("This preview supports rectilinear 1-D latitude/longitude grids.")
        latitude = np.asarray(lat_var[:], dtype=np.float64)
        longitude = np.asarray(lon_var[:], dtype=np.float64)
        if {"surf_u", "surf_v"}.issubset(ds.variables):
            u_name, v_name, kind = "surf_u", "surf_v", "Surface velocity"
        elif {"uwnd", "vwnd"}.issubset(ds.variables):
            u_name, v_name, kind = "uwnd", "vwnd", "Wind velocity"
        else:
            raise ValueError("No velocity pair found. Expected surf_u/surf_v or uwnd/vwnd.")
        u = _read_surface(ds[u_name], lat_var.dimensions[0], lon_var.dimensions[0])
        v = _read_surface(ds[v_name], lat_var.dimensions[0], lon_var.dimensions[0])
        timestamp = "Time not specified"
        records = 1
        if "time" in ds.variables:
            time = ds["time"]
            records = time.size
            if not records:
                raise ValueError("The file has no time records.")
            if hasattr(time, "units"):
                timestamp = num2date(time[0], time.units,
                                    calendar=getattr(time, "calendar", "standard")).isoformat()
        if latitude[0] > latitude[-1]:
            latitude, u, v = latitude[::-1], u[::-1], v[::-1]
        # Wrap and sort longitude so the maps use the usual -180..180 view.
        longitude = (longitude + 180) % 360 - 180
        order = np.argsort(longitude)
        longitude, u, v = longitude[order], u[:, order], v[:, order]
        curl = relative_vorticity(u, v, latitude, longitude)
        # Crop after differentiating, retaining native-grid neighbor stencils.
        iy = np.flatnonzero((latitude >= GULF_LATITUDE[0]) & (latitude <= GULF_LATITUDE[1]))
        ix = np.flatnonzero((longitude >= GULF_LONGITUDE[0]) & (longitude <= GULF_LONGITUDE[1]))
        if not iy.size or not ix.size:
            raise ValueError("This file does not cover the Gulf of Mexico preview region.")
        stride = max(1, int(np.ceil(max(iy.size, ix.size) / MAX_PREVIEW_SIDE)))
        lat_slice, lon_slice = slice(iy[0], iy[-1]+1, stride), slice(ix[0], ix[-1]+1, stride)
        sample = (lat_slice, lon_slice)
        return {
            "latitude": latitude[lat_slice].copy(), "longitude": longitude[lon_slice].copy(),
            "u": u[sample].copy(), "v": v[sample].copy(),
            "vorticity": curl[sample].copy(), "shape": u.shape, "stride": stride,
            "time": timestamp, "records": records, "kind": kind,
        }


def load_preview(root: PathInput, folder: str, filename: str) -> PreviewData:
    """Load a validated NetCDF basename from a year folder, using the cache.

    Only the first time record/level is shown. Invalid selections, unsupported
    variables/grids, and files without Gulf coverage raise ValueError. Filesystem
    and NetCDF read errors propagate for the UI to display. See PreviewData for
    array units, dimensions, and the read-only convention for cached results.
    """
    directory = checked_folder(root, folder)
    if not filename or Path(filename).name != filename or Path(filename).suffix.lower() not in {".nc", ".nc4", ".cdf"}:
        raise ValueError("Choose a NetCDF file from the selected folder.")
    path = directory / filename
    stat = path.stat()
    return _load_preview(str(path), stat.st_mtime_ns, stat.st_size)


def empty_figure(message: str = "Select a year, folder, and NetCDF file.") -> go.Figure:
    """Return an axis-free placeholder, also used to clear stale maps on error."""
    fig = go.Figure()
    fig.add_annotation(text=message, x=.5, y=.5, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(template="plotly_white", height=430, margin=dict(l=40, r=20, t=50, b=40),
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


def field_figures(data: PreviewData, folder: str) -> Tuple[go.Figure, go.Figure]:
    """Return Gulf speed and relative-vorticity figures without modifying data.

    Speed colors use m/s; fixed-length arrows encode direction only. Vorticity
    colors use 10^-5 s^-1 with symmetric limits. Per-record 99th percentiles set
    color limits, so identical colors across files need not mean equal values.
    ``folder`` contributes to Plotly's zoom-preservation key. No finite speed
    values raises ValueError; missing vorticity alone leaves its map blank.
    """
    lat, lon = data["latitude"], data["longitude"]
    speed = np.hypot(data["u"], data["v"])
    curl = data["vorticity"] * 1e5
    valid_speed, valid_curl = speed[np.isfinite(speed)], curl[np.isfinite(curl)]
    if not valid_speed.size:
        raise ValueError("The selected record has no finite velocity values.")
    speed_limit = max(float(np.percentile(valid_speed, 99)), .01)
    curl_limit = max(float(np.percentile(np.abs(valid_curl), 99)), .01) if valid_curl.size else 1

    def heatmap(
        z: FloatArray,
        title: str,
        colors: str,
        low: float,
        high: float,
        unit: str,
    ) -> go.Figure:
        fig = go.Figure(go.Heatmap(
            x=lon, y=lat, z=z, colorscale=colors, zmin=low, zmax=high,
            colorbar=dict(title=unit, thickness=15),
            hovertemplate="Lon %{x:.2f}°<br>Lat %{y:.2f}°<br>%{z:.3f} " + unit + "<extra></extra>",
            hoverongaps=False,
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=19)), template="plotly_white", height=490,
            margin=dict(l=60, r=30, t=60, b=50), plot_bgcolor="#dce3e8",
            xaxis=dict(title="Longitude (°)", range=list(GULF_LONGITUDE), autorange=False),
            yaxis=dict(title="Latitude (°)", range=list(GULF_LATITUDE), autorange=False),
            uirevision=f"gulf:{folder}:{title}", showlegend=False,
        )
        return fig

    velocity = heatmap(speed, "Gulf of Mexico · " + data["kind"].lower(), "Viridis", 0, speed_limit, "m/s")
    vorticity = heatmap(curl, "Gulf of Mexico · relative vorticity", "RdBu_r", -curl_limit, curl_limit, "10⁻⁵ s⁻¹")

    # Sparse, fixed-length arrows indicate direction only; the color gives speed.
    arrow_x, arrow_y = [], []
    sy, sx = max(1, len(lat)//22), max(1, len(lon)//35)
    for iy in range(sy//2, len(lat), sy):
        if abs(lat[iy]) > 80:
            continue
        for ix in range(sx//2, len(lon), sx):
            u, v = data["u"][iy, ix], data["v"][iy, ix]
            if not np.isfinite(u + v) or np.hypot(u, v) < .005:
                continue
            dx, dy = u / np.cos(np.deg2rad(lat[iy])), v
            length = np.hypot(dx, dy)
            dx, dy = dx / length * .25, dy / length * .25
            x0, y0 = lon[ix] - dx/2, lat[iy] - dy/2
            x1, y1 = x0 + dx, y0 + dy
            if (min(x0, x1) < GULF_LONGITUDE[0] or max(x0, x1) > GULF_LONGITUDE[1]
                    or min(y0, y1) < GULF_LATITUDE[0] or max(y0, y1) > GULF_LATITUDE[1]):
                continue
            arrow_x.extend([x0, x1, None, x1-.3*dx+.18*dy, x1, x1-.3*dx-.18*dy, None])
            arrow_y.extend([y0, y1, None, y1-.3*dy-.18*dx, y1, y1-.3*dy+.18*dx, None])
    velocity.add_trace(go.Scatter(x=arrow_x, y=arrow_y, mode="lines",
                                 line=dict(color="white", width=1), hoverinfo="skip"))
    return velocity, vorticity
