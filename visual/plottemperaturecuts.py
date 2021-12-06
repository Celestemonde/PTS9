#!/usr/bin/env python
# -*- coding: utf8 -*-
# *****************************************************************
# **       PTS -- Python Toolkit for working with SKIRT          **
# **       © Astronomical Observatory, Ghent University          **
# *****************************************************************

## \package pts.visual.plottemperaturecuts Plot planar cuts through the medium temperature in a SKIRT simulation
#
# This module offers functions to plot planar cuts through the medium temperature in a SKIRT simulation.
#

# -----------------------------------------------------------------

import logging
import matplotlib.pyplot as plt
import pts.simulation as sm
import pts.utils as ut

# -----------------------------------------------------------------

## This function creates a plot of the medium temperature cuts generated by DefaultXxxTemperatureCutsProbe
# or PlanarXxxTemperatureCutsProbe probes in a SKIRT simulation, where Xxx can refer to Dust, Gas, or Electron.
#
# The function accepts a single Simulation instance and it assumes that the simulation includes one or more
# DefaultXxxTemperatureCutsProbe or PlanarXxxTemperatureCutsProbe instances. If this is not the case,
# the function does nothing.
#
# By default, the figure is saved in the simulation output directory with a filename that includes the simulation
# prefix, the probe name, and the medium indicator, and has the ".pdf" filename extension. This can be overridden
# with the out* arguments as described for the pts.utils.savePath() function. In interactive mode (see the
# pts.utils.interactive() function), the figure is not saved and it is left open so that is displayed in notebooks.
#
def plotTemperatureCuts(simulation, *, outDirPath=None, outFileName=None, outFilePath=None,
                        figSize=None, interactive=None):

    # find the relevant probes
    probetypes = [ style + medium + "TemperatureCutsProbe" \
                    for style in ("Default", "Planar") for medium in ("Dust", "Gas", "Electron") ]
    probes = [ probe for probe in simulation.probes() if probe.type() in probetypes ]

    # iterate over the probes
    for probe in probes:
        # get the medium type of this probe, for use as part of the output file name
        medium = "dust"
        if "Gas" in probe.type(): medium = "gas"
        if "Electron" in probe.type(): medium = "elec"

        # load the temperature cuts and the range of the x and y axes
        # (there can be one to three cuts depending on symmetries)
        paths = probe.outFilePaths("{}_T_*.fits".format(medium))
        numcuts = len(paths)
        if not numcuts in (1,2,3):
            return
        cuts = [ path.stem.split("_")[-1] for path in paths ]
        frames = [ sm.loadFits(path) for path in paths ]
        grids = [ sm.getFitsAxes(path) for path in paths ]

        # determine the maximum temperature value to display
        Tmax = max([ frame.max() for frame in frames ])

        # setup the figure depending on the number of cuts
        if figSize is None: figSize = (8*numcuts,6)
        fig, axes = plt.subplots(ncols=numcuts, nrows=1, figsize=figSize)
        if numcuts==1: axes = [axes]

        # plot the cuts and set axis details for each
        for ax, cut, frame, (xgrid, ygrid) in zip(axes, cuts, frames, grids):
            extent = (xgrid[0].value, xgrid[-1].value, ygrid[0].value, ygrid[-1].value)
            im = ax.imshow(frame.value.T, vmin=0, vmax=Tmax.value, cmap='gnuplot', extent=extent,
                           aspect='equal', interpolation='bicubic', origin='lower')
            ax.set_xlim(xgrid[0].value, xgrid[-1].value)
            ax.set_ylim(ygrid[0].value, ygrid[-1].value)
            ax.set_xlabel(cut[0] + sm.latexForUnit(xgrid.unit), fontsize='large')
            ax.set_ylabel(cut[-1] + sm.latexForUnit(ygrid.unit), fontsize='large')
            ax.set_ylabel(cut[-1] + sm.latexForUnit(ygrid.unit), fontsize='large')

        # add a color bar
        fig.colorbar(im, ax=axes).ax.set_ylabel("T" + sm.latexForUnit(frame.unit), fontsize='large')

        # if not in interactive mode, save the figure; otherwise leave it open
        if not ut.interactive(interactive):
            saveFilePath = ut.savePath(simulation.outFilePath("{}_{}_T.pdf".format(probe.name(), medium)),
                                       (".pdf", ".png"),
                                       outDirPath=outDirPath, outFileName=outFileName, outFilePath=outFilePath)
            plt.savefig(saveFilePath, bbox_inches='tight', pad_inches=0.25)
            plt.close()
            logging.info("Created {}".format(saveFilePath))

# ----------------------------------------------------------------------
