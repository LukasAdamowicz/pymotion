# pykinematics
``pykinematics`` is an open-source Python package for estimating hip kinematics using both novel Magnetic and Inertial 
Measurement Unit (MIMU) wearable sensors and existing Optical Motion Capture (OMC) algorithms. The novel MIMU algorithms 
have been validated against OMC, and include novel methods for estimating sensor-to-sensor relative orientation and 
sensor-to-segment alignment.

## Documentation

Documentation including the below examples, and the API reference can be found at [pykinematics documentation](https://pykinematics.readthedocs.io/en/latest/)

## Requirements

- Python >=3.6
- Numpy
- Scipy
- h5py*

pip should automatically collect any uninstalled dependencies.

\* h5py is required to run the example code in `/scripts/example_code.py`, as the sample data 
provided (see *Example Usage*) is stored in the `.hdf` format. Pip will not catch and install
`h5py` as it is not used by ``pykinematics``, and must be installed manually to run the example code.

```shell script
pip install h5py
```
or if using Anaconda
```shell script
conda install -c anaconda h5py
```

## Installation

``pykinematics`` can be installed using pip:

```shell script
pip install pykinematics
```

Alternatively, you can clone this repository and install from source.

``pykinematics`` can be uninstalled by running
```shell script
pip uninstall pykinematics
```

## Running tests
Tests are implemented with [pytest](https://docs.pytest.org/en/latest/), and can be automatically run with:

```shell script
pytest --pyargs pykinematics.tests
```

Optionally add `-v` to increase verbosity.

If you don't want to run the integration tests (methods tests), use the following:
```shell script
python -m pykinematics.tests --no-integration
```

If you want to see coverage, the following can be run (assuming [coverage](https://coverage.readthedocs.io/en/v4.5.x/) is installed):

```shell script
coverage run -m pytest --pyargs pykinematics.tests
# generate the report
coverage report
# generate a HTML report under ./build/index.html
coverage html
```

## Example Usage

A full example script can be found in `/scripts/example_code.py`. This requires a sample 
data file, which can be downloaded from [Sample Data](https://www.uvm.edu/~rsmcginn/download/sample_data.h5)

`example_code.py` contains a helper function to load the data into Python.
Once the data is imported, the bulk of the processing is simple:

```python
import pykinematics as pk

static_calibration_data, star_calibration_data, walk_fast_data = <loaded sample data>

# define some additional keyword arguments for optimizations and orientation estimation
filt_vals = {'Angular acceleration': (2, 12)}

ka_kwargs = {'opt_kwargs': {'method': 'trf', 'loss': 'arctan'}}
jc_kwargs = dict(method='SAC', mask_input=True, min_samples=1500, opt_kwargs=dict(loss='arctan'), mask_data='gyr')
orient_kwargs = dict(error_factor=5e-8, c=0.003, N=64, sigma_g=1e-3, sigma_a=6e-3)

mimu_estimator = pk.ImuAngles(gravity_value=9.8404, filter_values=filt_vals, joint_center_kwargs=jc_kwargs,
                              orientation_kwargs=orient_kwargs, knee_axis_kwargs=ka_kwargs)

# calibrate the estimator based on Static and Star Calibration tasks
mimu_estimator.calibrate(static_calibration_data, star_calibration_data)

# compute the hip joint angles for the Fast Walking on a treadmill
left_hip_angles, right_hip_angles = mimu_estimator.estimate(walk_fast_data, return_orientation=False)
```

Right hip angles from the sample data for walking fast:

![Sample right hip angles](https://github.com/M-SenseResearchGroup/pymotion/blob/master/images/sample_data_right_hip_angles.png "Sample right hip joint angles")
