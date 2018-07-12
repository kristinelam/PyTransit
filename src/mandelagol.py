## PyTransit
## Copyright (C) 2010--2015  Hannu Parviainen
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import numpy as np
import pytransit.mandelagol_py as ma
import pytransit.orbits as of
from .tm import TransitModel

class MandelAgol(TransitModel):
    """Linear and quadratic Mandel-Agol transit models (ApJ 580, L171-L175 2002).

    This class wraps the Fortran implementations of the linear and quadratic Mandel & Agol
    transit models.
    """

    models = 'uniform quadratic interpolated_quadratic chromosphere'.split()
    
    def __init__(self, nldc=2, nthr=0, interpolate=False, supersampling=1, exptime=0.020433598, eclipse=False, klims=(0.07,0.13), nk=128, nz=256, model='quadratic', **kwargs):
        """Initialise the model.

        Args:
            nldc: Number of limb darkening coefficients, can be either 0 (no limb darkening) or 2 (quadratic limb darkening).
            nthr: Number of threads (default = 0).
            interpolate: If True, evaluates the model using interpolation (default = False).
            supersampling: Number of subsamples to calculate for each light curve point (default=0).
            exptime: Integration time for a single exposure, used in supersampling default=(0.02).
            eclipse: If True, evaluates the model for eclipses. If false, eclipses are filtered out (default = False). 
            klims: Minimum and maximum radius ratio if interpolation is used as (kmin,kmax).
            nk: Interpolation table resolution in k.
            nz: Interpolation table resolution in z.
        """
        assert model in self.models, 'Unknown MA model {}'.format(model)
        assert nldc in [0,2], 'Number of limb darkening coefficients must be either 0 or 2'

        super(MandelAgol, self).__init__(nldc, nthr, interpolate, supersampling, exptime, eclipse, **kwargs)
        self.interpolate = interpolate or kwargs.get('lerp', False)

        if model == 'chromosphere':
            self._eval = self._eval_chromosphere
        else:
            if model == 'uniform' or nldc == 0:
                self._eval = self._eval_uniform
            else:
                if model=='interpolated_quadratic' or self.interpolate:
                    self.ed,self.le,self.ld,self.kt,self.zt = ma.calculate_interpolation_tables(klims[0],klims[1],nk,nz)
                    self.klims = klims
                    self.nk = nk
                    self.nz = nz
        
                self._eval = self._eval_quadratic


    def _eval_uniform(self, z, k, u, c):
        """Wraps the Fortran implementation of a transit over a uniform disk

            Args:
                z: Array of normalised projected distances.
                k: Planet to star radius ratio.
                u: Array of limb darkening coefficients, not used.
                c: Array of contamination values as [c1, c2, ... c_npb].
                update: Not used.

            Returns:
                An array of model flux values for each z.
        """
        return ma.eval_uniform(z, k, c)

    
    def _eval_chromosphere(self, z, k, u, c):
        """Wraps the Fortran implementation of a transit over a uniform disk

            Args:
                z: Array of normalised projected distances.
                k: Planet to star radius ratio.
                c: Array of contamination values as [c1, c2, ... c_npb].

            Returns:
                An array of model flux values for each z.
        """
        return ma.eval_chromosphere(z, k, c)

    
    def _eval_quadratic(self, z, k, u, c):
        """Wraps the Fortran implementation of the quadratic Mandel-Agol model

          Args:
                z: Array of normalised projected distances
                k: Planet to star radius ratio
                u: Array of limb darkening coefficients.
                c: Array of contamination values as [c1, c2, ... c_npb]
                update: Not used.

        """
        u = np.asarray(u).ravel()
        npb = len(u)//2
        if not isinstance(c, np.ndarray) or c.size != npb:
            c = c*np.ones(npb)
            
        if self.interpolate:
            return ma.eval_quad_ip(z, k, u, c, self.ed, self.ld, self.le, self.kt, self.zt)
        else:
            return ma.eval_quad(z, k, u, c)


    def __call__(self, z, k, u, c=0.0):
        """Evaluates the model for the given z, k, and u. 
        
        Evaluates the transit model given an array of normalised distances, a radius ratio, and
        a set of limb darkening coefficients.
        
        Args:
            z: Array of normalised projected distances.
            k: Planet to star radius ratio.
            u: Array of limb darkening coefficients.
            c: Contamination factor (fraction of third light), optional.
           
        Returns:
            An array of model flux values for each z.
        """
        flux = self._eval(z, k, u, c)
        return flux.ravel() if flux.shape[0] == 1 else flux


    
class MAChromosphere(MandelAgol):
    def __init__(self, nthr=0, supersampling=1, exptime=0.020433598):
        super().__init__(model='chromosphere', nthr=nthr, supersampling=supersampling, exptime=exptime)

    def __call__(self, z, k, c=0, **kwargs):
        return self._eval(z, k, [], c)

    def evaluate(self, t, k, t0, p, a, i, e=0., w=0., c=0.):
        return super().evaluate(t, k, [], t0, p, a, i, e, w)


    
class MAUniform(MandelAgol):
    def __init__(self, nthr=0, supersampling=1, exptime=0.020433598, eclipse=False):
        super().__init__(model='uniform', nldc=0, nthr=nthr, supersampling=supersampling, exptime=exptime, eclipse=eclipse)
