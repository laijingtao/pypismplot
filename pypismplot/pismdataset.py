"""
An interface to PISM NetCDF files
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from .colors import default_cmaps

sec_year = 365*24*3600.


class PISMDataset():
    """An interface to PISM NetCDF files
    Provide simple plot methods for quick visualization of PISM results.
    """
    def __init__(self, file_name, *args, **kwargs):
        self.data =  Dataset(file_name, *args, **kwargs)
        self._file_name = file_name
        try:
            self.x = self.data.variables['x'][:]/1000.0  # km
            self.y = self.data.variables['y'][:]/1000.0
        except:
            self.x = None
            self.y = None
        try:
            self.time = self.data.variables['time'][:]/sec_year # yr
        except:
            self.time = None

    def _get_axes(self, ax=None):
        if ax is None:
            ax = plt.gca()
        return ax

    def _add_mask(self, z, t=None, mask_var=None, mask_thold=None, *args, **kwargs):
        if mask_var is None or mask_thold is None:
            return z
        if mask_var in self.data.variables:
            mask_data = self._get_2d_data(mask_var, t)
            z[np.where(mask_data<=mask_thold)] = np.nan
            z = np.ma.masked_where(np.isnan(z), z)
            np.ma.set_fill_value(z, np.nan)
        else:
            sys.exit("pypismplot error: Cannot find {} in {}".format(mask_var, self._file_name))

        return z
    
    def _get_2d_data(self, var_name, t=None):
        var = self.data.variables[var_name]
        time = self.time

        if t is None:
            if len(var.shape)==2:
                z = var[:]
            else:
                if len(var)==1:
                    z = var[:][0]
                else:
                    sys.exit("pypismplot error: "\
                             +"t is required because {} has time dimension".format(self._file_name))
        else:
            try:
                z = var[np.where(time==t)]
            except:
                sys.exit("pypismplot error: Cannot find t={} in {}".format(t, self._file_name)) 
        z = z.squeeze()

        return z

    def close(self):
        self.data.close()
    
    def get_masked_data(self, var_name, t=None, mask_var=None, mask_thold=None):
        """Extract data with mask

        Parameters
        ----------
        var_name : str
            Variable name to plot
        t : float, optional
            When the PISM data contains time dimension, t is required
        mask_var : str, optional
            Variable to create mask
        mask_thold : float, optional
            Variable threshold to create mask
        """

        z = self._get_2d_data(var_name, t)
        z = self._add_mask(z, t=t, mask_var=mask_var, mask_thold=mask_thold)

        return z

    def pcolormesh(self, var_name, ax=None, *args, **kwargs):
        """Plot mapview of PISM data

        Parameters
        ----------
        var_name : str
            Variable name to plot
        ax : matplotlib axes
            Axes where data are potted
        t : float, optional
            When the PISM data contains time dimension, t is required
        mask_var : str, optional
            Variable to create mask
        mask_thold : float, optional
            Variable threshold to create mask
        title : str, optional
            Title, default is long_name of the variable,
            use var_name if long_name does not exist,
            set None to disable
        allow_colorbar : bool, optional
            If ture, show colorbar, default False

        For other parameters, see matplotlib doc
        """
        t = kwargs.pop('t', None)
        mask_var = kwargs.pop('mask_var', None)
        mask_thold = kwargs.pop('mask_thold', None)
        try:
            title = self.data.variables[var_name].long_name
        except:
            title = var_name
        title = kwargs.pop('title', title)
        allow_colorbar = kwargs.pop('allow_colorbar', False)

        ax = self._get_axes(ax)
        ax.set_aspect(aspect='equal', adjustable='box-forced')

        xx, yy = np.meshgrid(self.x, self.y)
        z = self.get_masked_data(var_name, t=t, mask_var=mask_var, mask_thold=mask_thold)
        im = ax.pcolormesh(xx, yy, z,
                           cmap=kwargs.pop('cmap', default_cmaps.get(var_name)),
                           **kwargs)

        ax.set_xlabel('X (km)')
        ax.set_ylabel('Y (km)')
        if title is not None:
            ax.set_title(title)
        if allow_colorbar:
            cbar = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.6)
            try:
                cbar.set_label(self.data.variables[var_name].units)
            except:
                pass

        return im

    def plot_time_series(self, var_name, ax=None, *args, **kwargs):
        """Plot time series of PISM data

        Parameters
        ----------
        var_name : str
            Variable name to plot
        ax : matplotlib axes
            Axes where data are potted
        time_range : list, optional
            Range of time shown in figure 
        ylabel : str, optional
            Label of Y axis, default is long_name of the variable,
            use var_name if long_name does not exist,
            set None to disable
        """
        time_range = kwargs.pop('time_range', None)
        try:
            ylabel = self.data.variables[var_name].long_name
        except:
            ylabel = var_name
        ylabel = kwargs.pop('title', ylabel)

        ax = self._get_axes(ax)

        time = self.time
        if time is None:
            sys.exit("pypismplot error: "\
                     +"{} does not have time dimension.".format(self._file_name))
        plot_data = self.data.variables[var_name][:]
        im = ax.plot(time/1000.0, plot_data, **kwargs)
        
        ax.set_xlabel('Time (kyr)')
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if time_range is not None:
            ax.set_xlim(time_range)

        return im
