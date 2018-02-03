"""
Extension for netcdf dataset
"""

import sys
import numpy as np
from netCDF4 import Dataset

sec_year = 365*24*3600.

class SurfDatasetError(Exception):
    """Raise NetCDFDataError if the netcdf file does not have required variables or dimensions.
    """
    pass

class SurfDataset():
    """Dataset for surface processes modeling based on netCDF Dataset class
    """
    def __init__(self, nc_file, *args, **kwargs):
        self.ncdataset =  Dataset(nc_file, *args, **kwargs)
        self._nc_file = nc_file

        try:
            self.x = self.ncdataset.variables['x'][:] #m
        except:
            raise SurfDatasetError('Missing dimension x in {}'.format(self._nc_file))
        try:
            self.y = self.ncdataset.variables['y'][:] #m
        except:
            raise SurfDatasetError('Missing dimension y in {}'.format(self._nc_file))

        self.row = len(self.y)
        self.col = len(self.x)
        self.shape = [self.row, self.col]

        self.node_x = np.zeros((self.row, self.col))
        for j in range(self.col):
            self.node_x[:, j] = self.x[j]
        self.node_y = np.zeros((self.row, self.col))
        for i in range(self.row):
                self.node_y[i, :] = self.y[i]
        try:
            self.time = self.ncdataset.variables['time'][:]/sec_year # yr
        except:
            self.time = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.ncdataset.close()