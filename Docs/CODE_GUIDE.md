# WorldLitter code guide

WorldLitter releases particles at coastal and river locations, transports them
with surface velocity fields, and exports trajectories for maps and web displays.
A separate reporting workflow formats **externally computed** country statistics;
it does not calculate those statistics from this repository's trajectories.

For the visual overview, open [the HTML summary](Summary/index.html). This guide
documents the code contracts, configuration, and current execution constraints.

## Start with the local data viewer

From the repository root, using the existing local environment:

```bash
source /home/olmozavala/uv/envs/aieoas/bin/activate
python 0_Summary_Start_Here.py --port 8060
```

Open <http://127.0.0.1:8060/>. The viewer requires Dash >= 3.4, NumPy, netCDF4,
and Plotly. It reads mounted data and provides a command to copy; it does not
mount storage or execute simulation jobs. The mount command is:

```bash
sudo sshfs ozavala@skynet.coaps.fsu.edu:/nexsan /nexsan/
```

The data root is `/nexsan/people/xbxu/HYCOM/GLBv0.08` (case-sensitive).
Year folders are discovered dynamically. `YEAR` holds currents, `YEARc` holds
currents plus 0.01 times wind, and `YEARw` holds wind alone. Use `YEARc` for the
intended combined-forcing runs; those velocities already include the wind term.
The viewer currently defaults to bare `YEAR` when that folder exists, so select
the `c` variant explicitly. Previous/Next follow lexical filename order.

## How the modules connect

| Stage | Main code | Inputs → outputs |
| --- | --- | --- |
| Release attribution | `0_1_Combine_Locations_with_Countries_and_Oceans.py` | Release coordinates and GIS boundaries → country/ocean particle-index CSV |
| Local inspection | `0_Summary_Start_Here.py`, `utils/hycom_preview.py` | Mounted forcing NetCDF → speed and relative-vorticity maps |
| Simulation orchestration | `1_WorldLitter.py` | Dates, feature flags, configuration → one run or successive restart segments |
| One simulation segment | `models/models.py` | Forcing, releases or a restart file → Parcels trajectory output |
| Field preparation | `utils/io_hycom.py` | Year folders and auxiliary fields → file list and modified Parcels FieldSet |
| Particle movement | `mykernels/custom_particles.py`, `mykernels/wl_kernels.py` | Particle state and sampled fields → updated particle state |
| Restart merge | `2_MergeRuns.py` | Segments from one release → merged trajectory NetCDF |
| Extend existing runs | `7_Merge_Merged_Adding_New_Years.py` | Previous/new monthly-release outputs → concatenated observations |
| Visualization/export | `3_Show_Output.py`, `4_OceanParcels_to_JSON_and_ZIP_V2.py` | Trajectories and country indices → maps or binary web data with text headers |
| Spatial aggregation | `5_MakeHistogramNcWMS.py` | Saved trajectory positions → gridded accumulated-location products |
| Storage conversion | `0_UpdateToZarr.py` | NetCDF → consolidated Zarr store |
| Country reporting | `Tables_1_Make_Tables_by_Country.py`, `Tables_2_*.py` | Upstream text statistics → JSON/CSV, tables, figures, and reports |

## Configuration and simulation setup

The simulation imports `get_op_config()` from `config/MainConfig.py`, a local,
Git-ignored configuration. The tracked `MainConfigExample.py`,
`MainConfigExampleCOAPS.py`, and `MainConfigHPC.py` show historical settings;
their absolute paths require review for the machine and dataset being used.

**Existing compatibility issue:** `config/params.py` defines `GlobalModel`, while
the simulation, restart merger, and several examples import `WorldLitter`.
Those imports currently fail. Reconcile the enum name and its consumers before
running simulations; changing the documentation and annotations does not fix
this mismatch. Configuration keys are enum members, not strings.

| Configuration member | Expected value | Use |
| --- | --- | --- |
| `base_folder` | Directory path | Parent of forcing folders such as `2010` and `2010c` |
| `loc_folder` | Directory path | Parent of release-coordinate files |
| `lat_files`, `lon_files` | Ordered filename sequences | Matching latitude/longitude vectors in degrees; file order defines particle order |
| `output_folder` | Existing writable directory | Trajectory output location |
| `output_file` | String appended to a generated name | Restart/merge filename suffix; verify that it matches actual Parcels output naming |
| `dt` | `datetime.timedelta` | Integration step; the unbeaching threshold assumes a positive step |
| `output_freq` | `datetime.timedelta` | Interval between saved observations |
| `repeat_release` | Parcels `repeatdt` value | Repeated-release interval; historical configurations use `False` to disable it, so check the installed Parcels API |
| `unbeach_file` | NetCDF path | Auxiliary `unBeachU`/`unBeachV` grid; the runner reads this config key even when unbeaching is disabled |
| `years` | Integer year sequence | Used by some scripts; `sequential()` instead derives forcing years from its start/end dates |
| `countries_file` | CSV path | Country-to-particle indices used by downstream exporters |
| `stats_folder`, `output_folder_web` | Directory paths | Country-report inputs and web outputs used by selected scripts |

`wind_factor` remains an enum key, but the simulation selects precombined `YEARc`
files through the `winds` flag; it does not apply this configuration value to the
velocities. Diffusion currently uses the constant `Kh = 1 m²/s` in the runner.

The legacy simulation uses Parcels interfaces including `ErrorCode`,
`parcels.rng`, and `ParticleFile.export()`. There is no pinned dependency
environment in this checkout. The viewer's working environment is not evidence
that these older simulation interfaces are compatible. `eoas_pyutils` is also
registered as a submodule but absent from the current working tree.

### Input and output contracts

Simulation forcing maps NetCDF `surf_u` and `surf_v` to eastward/northward
velocity, with coordinates `latitude`, `longitude`, and `time`. Coordinate CSV
pairs must have compatible lengths and ordering. The runner reads release CSVs
even when restoring particles from an existing trajectory file.

`read_files()` searches each requested `YEAR` or `YEARc` directory. It skips
missing directories and does not filter directory entries by extension. For
date filtering, it expects the **fifth underscore-separated filename token** to
begin with `YYYYMMDD`. Parsed dates are midnight, so a nonzero start hour can
exclude that day's files. Confirm this convention for each forcing variant;
the viewer lists files without imposing this date-token convention.

The segment merger expects `time`, `trajectory`, `lat`, `lon`, and `z` with
`(traj, obs)` dimensions and matching particle order between files. Unbeaching
runs also require `beached` and `beached_count`. The binary exporter depends on
the country-index CSV matching that same release ordering. Despite its name,
script 4's active export is binary data plus text headers, not JSON.

### Running and restarting

After resolving configuration and library compatibility, the CLI contract is:

```text
python 1_WorldLitter.py START END WINDS DIFFUSION UNBEACHING NAME
python 1_WorldLitter.py START END WINDS DIFFUSION UNBEACHING NAME RESTART_FILE EXECUTION_DAYS
python 2_MergeRuns.py START END UNBEACHING NAME EXECUTION_DAYS
```

Dates use `YYYY-MM-DD:HH`, for example `2010-01-01:00`. Flags accept `yes`,
`true`, `t`, or `1` as true, ignoring case; other strings are false. The two
optional restart arguments must be supplied together. A missing restart path
starts a fresh release. `EXECUTION_DAYS` must be positive and end must follow
start; the current functions do not enforce these conditions.

Adjacent restart segments repeat their boundary observation. `2_MergeRuns.py`
drops the first observation from every segment after the first. It currently
requires at least two segments; a single-segment interval leaves accumulation
variables uninitialized. `7_Merge_Merged_Adding_New_Years.py` retains all
observations, so inspect overlap when appending existing merged runs. It deletes
an existing destination before processing that pair of inputs.

### Beaching state and movement order

The custom particle's integer `beached` state progresses through `0` (at sea),
`1` (after advection), `2` (after diffusion), `3` (needs unbeaching), and `4`
(stopped by the custom movement kernels). Beach testing uses near-zero sampled
velocity rather than a coastline intersection. The runner orders kernels as
advection, optional beach test/unbeaching, optional diffusion and beach retest,
then longitude wrapping.

`beached_count` counts cumulative unbeaching attempts. Its ten-day-equivalent
threshold does not measure consecutive days ashore because the counter is never
reset. State-4 particles are retained; the deletion code is commented out.
The out-of-bounds recovery callback also assigns state 4 and therefore requires
the custom variable, although the runner registers it for plain `JITParticle`
as well. That existing recovery mismatch needs review before production runs.

## NetCDF preview: units, arrays, and cache

`load_preview()` prefers `surf_u`/`surf_v`, falling back to `uwnd`/`vwnd`. It
reads index zero on time and other nonspatial dimensions, converts masked values
to NaN, normalizes the spatial arrays to `(latitude, longitude)`, reverses
descending latitude, and wraps/sorts longitude into `[-180, 180)`.

`relative_vorticity()` computes the vertical curl on a sphere:

```text
ζ = [∂v/∂λ − ∂(u cos φ)/∂φ] / (R cos φ)
```

Here φ and λ are radians, R is 6,371,000 m, and u/v are in m/s. The result is
relative vorticity in s⁻¹; it contains no planetary rotation term. Coordinates
must be one-dimensional, increasing after normalization, and have at least
three points per axis. A complete longitude cycle receives periodic seam
derivatives. Missing data and the pole singularity are masked.

Derivatives are computed on the native grid **before** cropping to 99°W–79°W,
18°N–32°N. The crop is thinned only if needed to keep each displayed side at most
650 points. `PreviewData` documents the returned arrays and metadata. NetCDF
reads are serialized with a lock; a three-entry cache stores cropped results,
keyed by path, modification time, and size. Callers must treat cached arrays as
read-only. This limits retained display data, not peak memory during a full read.

Speed is colored in m/s and arrows show direction only. Vorticity is plotted in
10⁻⁵ s⁻¹. Each file uses its own 99th-percentile color limits, so compare numeric
values rather than colors alone between files. Read failures clear both plots.

## Country-statistics parsing

The main table converter reads semicolon-delimited `_from_` and `_to_` reports;
separate functions support the older fixed-width no-decay format. A `from`
report describes waste originating in a country and its destinations; a `to`
report describes arriving waste and its sources. Source quantities and
percentages are preserved without rescaling; consult each scenario's header
for its reporting period and mass-unit convention.

Parser functions return `(report, country_name)`. Caught errors return
`(-1, country_name)`, but header parsing outside their try blocks can still
raise. The converter can retain the `-1` sentinel in JSON, so downstream readers
must check report validity. Countries with no `from` key are removed.
`ReachedTablesData.json` nests `from`/`to` reports under country names; each
direction contains totals and lists of `{name, tons, perc}` records. Its CSV
companion contains human-readable blocks, not a single normalized table.

## Maintaining and checking the code

Public helpers and orchestration functions now document their input/output
contracts. The viewer uses `TypedDict` for its preview and callback payloads,
and NumPy annotations describe floating arrays. Legacy configuration mappings
use `Mapping[Enum, Any]` because values genuinely mix paths, lists, time intervals,
and flags; the table above supplies the key-specific contract. Annotations do
not replace validation. JIT kernel signatures remain unannotated to preserve
compatibility with the legacy Parcels source parser.

Run the focused numerical and input-handling checks without a mounted dataset:

```bash
source /home/olmozavala/uv/envs/aieoas/bin/activate
python -m pytest -q tests/test_hycom_preview.py
```

These cover spherical solid-body rotation, periodic derivatives, missing values,
folder discovery, and synthetic NetCDF axis reordering/cropping. They do not
validate a full Parcels simulation, MPI job, table scenario, or web deployment.
