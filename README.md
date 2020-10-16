# fordpass-python

This is a basic Python wrapper around the FordPass APIs. It's more or less a straight port of @d4v3y0rk's NPM module [d4v3y0rk/ffpass](https://github.com/d4v3y0rk/ffpass-module) - props to him for his work figuring out the relevant API requests needed.

## Features

* Automatically auth & re-fetches tokens once expired
* Get status of the vehicle (this returns a ton of info about the car: lat/long, oil, battery, fuel, odometer, tire pressures, open windows and a bunch of other stuff that may/may not apply to your car, e.g. charge level, diesel filters.)
* Start the engine (if supported)
* Stop the engine (if supported)
* Lock the doors
* Unlock the doors

## Demo

To test the libary there is a demo script `demo.py`.

```
demo.py USERNAME PASSWORD VIN
```

e.g.

```
demo.py test@test.com mypassword WX12345678901234
```