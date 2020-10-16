[![PyPI version](https://badge.fury.io/py/fordpass.svg)](https://badge.fury.io/py/fordpass)

# fordpass-python

This is a basic Python wrapper around the FordPass APIs. It's more or less a straight port of @d4v3y0rk's NPM module [d4v3y0rk/ffpass](https://github.com/d4v3y0rk/ffpass-module) - props to him for his work figuring out the relevant API requests needed.

## Features

* Automatically auth & re-fetches tokens once expired
* Get status of the vehicle (this returns a ton of info about the car: lat/long, oil, battery, fuel, odometer, tire pressures, open windows and a bunch of other stuff that may/may not apply to your car, e.g. charge level, diesel filters.)
* Start the engine (if supported)
* Stop the engine (if supported)
* Lock the doors
* Unlock the doors

## Install
Install using pip:

```
pip install fordpass
```

## Demo

To test the libary there is a demo script `demo.py`.

```
demo.py USERNAME PASSWORD VIN
```

e.g.

```
demo.py test@test.com mypassword WX12345678901234
```

## Publishing new versions of this package

1. Bump the version number inside `setup.py`.
2. Build the package: `python setup.py sdist bdist_wheel`.
3. Upload to TestPyPi using `twine upload --repository-url https://test.pypi.org/legacy/ dist/*` and verify everything is as expected.
4. Upload to PyPi using `twine upload dist/*`.
5. All done!