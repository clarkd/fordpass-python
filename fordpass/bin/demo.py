#!/usr/bin/env python

"""
Simple script to demo the API
"""

import sys, os, logging, time
from fordpass import Vehicle

if __name__ == "__main__":

    if len(sys.argv) != 4:
        raise Exception('Must specify Username, Password and VIN as arguments, e.g. demo.py test@test.com password123 WX231231232')
    else:            
        r = Vehicle(sys.argv[1], sys.argv[2], sys.argv[3]) # Username, Password, VIN

        print(r.status()) # Print the status of the car

        # r.unlock() # Unlock the doors

        # time.sleep(10) # Wait 10 seconds

        # r.lock() # Lock the doors