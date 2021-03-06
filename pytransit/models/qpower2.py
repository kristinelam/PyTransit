# -*- coding: utf-8 -*-
#  PyTransit: fast and easy exoplanet transit modelling in Python.
#  Copyright (C) 2010-2019  Hannu Parviainen
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""QPower2 transit model.

This module offers the QPower2 class implementing the transit model by Maxted & Gill (ArXIV:1812.01606).
"""
from numpy import squeeze, ndarray, array

from .numba.qpower2_nb import qpower2_model
from .transitmodel import TransitModel

__all__ = ['QPower2Model']

class QPower2Model(TransitModel):
    """QPower2 transit model (Maxted & Gill, ArXIV:1812.01606).
    """

    def evaluate_ps(self, k: float, ldc: ndarray, t0: float, p: float, a: float, i: float, e: float = 0., w: float = 0.) -> ndarray:
        assert self.time is not None, "Need to set the data before calling the transit model."
        pvp = array([[k, t0, p, a, i, e, w]])
        flux = qpower2_model(self.time, pvp, ldc, self.lcids, self.pbids, self.nsamples, self.exptimes, self._es, self._ms, self._tae)
        return squeeze(flux)

    def evaluate_pv(self, pvp: ndarray, ldc: ndarray) -> ndarray:
        assert self.time is not None, "Need to set the data before calling the transit model."
        flux = qpower2_model(self.time, pvp, ldc, self.lcids, self.pbids, self.nsamples, self.exptimes, self._es, self._ms, self._tae)
        return squeeze(flux)

