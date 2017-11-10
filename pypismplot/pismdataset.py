"""
An interface to PISM NetCDF files
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from .colors import default_cmaps

sec_year = 365*24*3600.

def _get_axes(ax=None):
    if ax is None:
        ax = plt.gca()
    return ax

class PISMDataset():
    def __init__(self, file_name, *args, **kwargs):
        self.data =  Dataset(file_name, *args, **kwargs)
        self._file_name = file_name
        self._x = self.data.variables['x'][:]/1000.0  # km
        self._y = self.data.variables['y'][:]/1000.0

    def _add_mask(self, z, t=None, mask_var=None, mask_thold=None, *args, **kwargs):
        if mask_var is None or mask_thold is None:
            return z
        if mask_var in self.data.variables:
            mask_data = self._get_2d_data(mask_var, t)
            z[np.where(mask_data<=mask_thold)] = np.nan
            z = np.ma.masked_where(np.isnan(z), z)
            np.ma.set_fill_value(z, np.nan)
        else:
            sys.exit("Cannot find {} in {}".format(mask_var, self._file_name))

        return z
    
    def _get_2d_data(self, var_name, t=None):
        var = self.data.variables[var_name]
        time = self.data.variables['time'][:]/sec_year

        if len(var.shape)==2:
            z = var[:]
        else:
            try:
                z = var[np.where(time==t)]
            except:
                sys.exit("Cannot find t={} in {}".format(t, self._file_name)) 
        z = z.squeeze()

        return z

    def close(self):
        self.data.close()
    
    def get_masked_data(self, var_name, t=None, mask_var=None, mask_thold=None):
        z = self._get_2d_data(var_name, t)
        z = self._add_mask(z, t=t, mask_var=mask_var, mask_thold=mask_thold)

        return z

    def pcolormesh(self, var_name, ax=None, *args, **kwargs):
        ax = _get_axes(ax)
        ax.set_aspect(aspect='equal', adjustable='box-forced')
        x, y = self._x, self._y
        xx, yy = np.meshgrid(x, y)
        t = kwargs.pop('t', None)
        mask_var = kwargs.pop('mask_var', None)
        mask_thold = kwargs.pop('mask_thold', None)
        z = self.get_masked_data(var_name, t=t, mask_var=mask_var, mask_thold=mask_thold)
        im = ax.pcolormesh(xx, yy, z,
                           cmap=kwargs.pop('cmap', default_cmaps.get(var_name)),
                           **kwargs)
        return im
                          
