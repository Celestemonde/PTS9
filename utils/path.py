#!/usr/bin/env python
# -*- coding: utf8 -*-
# *****************************************************************
# **       PTS -- Python Toolkit for working with SKIRT          **
# **       © Astronomical Observatory, Ghent University          **
# *****************************************************************

## \package pts.utils.path Special paths related to PTS
#
# This module allows retrieving some special paths related to PTS, such as for example
# the path to the pts repository.
#

# -----------------------------------------------------------------

import inspect
import pathlib

# -----------------------------------------------------------------

## This function returns the absolute path to the top-level directory of the pts repository
# as a pathlib.Path object.
def pts():
    return pathlib.Path(inspect.getfile(inspect.currentframe())).parent.parent

# -----------------------------------------------------------------
