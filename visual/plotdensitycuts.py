#!/usr/bin/env python
# -*- coding: utf8 -*-
# *****************************************************************
# **       PTS -- Python Toolkit for working with SKIRT          **
# **       © Astronomical Observatory, Ghent University          **
# *****************************************************************

## \package pts.visual.plotdensitycuts Plot planar cuts through the medium density in a SKIRT simulation
#
# This module offers functions to plot planar cuts through the medium density in a SKIRT simulation,
# allowing a visual comparison between the theoretical and spatially gridded medium density distribution.
#

# -----------------------------------------------------------------

import logging
import matplotlib.colors
import matplotlib.pyplot as plt
import pts.simulation as sm
import pts.utils as ut

# -----------------------------------------------------------------

## This function creates plots of media density cuts generated by the DefaultMediaDensityCutsProbe or
# PlanarMediaDensityCutsProbe in a SKIRT simulation, allowing a visual comparison between the theoretical
# and spatially gridded medium density distribution.
#
# The function accepts a single Simulation instance and it assumes that the simulation includes one or more
# DefaultMediaDensityCutsProbe or PlanarMediaDensityCutsProbe instances. If this is not the case, the function
# does nothing.
#
# By default, the figures are saved in the simulation output directory with a filename that includes the simulation
# prefix, the probe name, and the medium indicator, and has the ".pdf" filename extension. The output directory
# can be overridden as described for the pts.utils.savePath() function. In interactive mode (see the
# pts.utils.interactive() function), the figures are not saved and are left open for display in notebooks.
#
def plotMediaDensityCuts(simulation, decades=5, *, outDirPath=None, figSize=(18, 6), interactive=None):

    # find the relevant probes
    probes = [ probe for probe in simulation.probes() \
               if probe.type() in ("DefaultMediaDensityCutsProbe", "PlanarMediaDensityCutsProbe") ]

    # iterate over them
    for probe in probes:
        for medium in ("dust", "elec", "gas"):
            for cut in ("xy", "xz", "yz"):

                # load the theoretical and gridded cuts for the requested medium and cut plane
                tPaths = probe.outFilePaths("{}_t_{}.fits".format(medium,cut))
                gPaths = probe.outFilePaths("{}_g_{}.fits".format(medium,cut))
                if len(tPaths) == 1 and len(gPaths) == 1:
                    tFrame = sm.loadFits(tPaths[0])
                    gFrame = sm.loadFits(gPaths[0])

                    # determine the range of the x and y axes
                    xgrid, ygrid = sm.getFitsAxes(tPaths[0])

                    # determine the range of density values to display and clip the data arrays
                    vmax = max(tFrame.max(), gFrame.max())
                    vmin = vmax / 10**decades
                    tFrame[ tFrame<vmin ] = vmin
                    gFrame[ gFrame<vmin ] = vmin

                    # setup the figure
                    fig, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=figSize)

                    # plot the cuts and a color bar (logarithmic normalizer crashes if all values are zero)
                    if vmax>0:
                        normalizer = matplotlib.colors.LogNorm(vmin.value, vmax.value)
                    else:
                        normalizer = matplotlib.colors.Normalize(vmin.value, vmax.value)
                    extent = (xgrid[0].value, xgrid[-1].value, ygrid[0].value, ygrid[-1].value)
                    im = ax1.imshow(tFrame.value.T, norm=normalizer, cmap='gnuplot', extent=extent,
                                    aspect='equal', interpolation='bicubic', origin='lower')
                    fig.colorbar(im, ax=(ax1,ax2)).ax.set_ylabel("density" + sm.latexForUnit(tFrame.unit),
                                                                 fontsize='large')
                    ax2.imshow(gFrame.value.T, norm=normalizer, cmap='gnuplot', extent=extent,
                               aspect='equal', interpolation='bicubic', origin='lower')

                    # set axis details
                    ax1.set_xlim(xgrid[0].value, xgrid[-1].value)
                    ax1.set_ylim(ygrid[0].value, ygrid[-1].value)
                    ax2.set_xlim(xgrid[0].value, xgrid[-1].value)
                    ax2.set_ylim(ygrid[0].value, ygrid[-1].value)
                    ax1.set_xlabel(cut[0] + sm.latexForUnit(xgrid.unit), fontsize='large')
                    ax1.set_ylabel(cut[-1] + sm.latexForUnit(ygrid.unit), fontsize='large')
                    ax2.set_xlabel(cut[0] + sm.latexForUnit(xgrid.unit), fontsize='large')
                    ax2.set_ylabel(cut[-1] + sm.latexForUnit(ygrid.unit), fontsize='large')

                    # if not in interactive mode, save the figure; otherwise leave it open
                    if not ut.interactive(interactive):
                        defSavePath = simulation.outFilePath("{}_{}_{}.pdf".format(probe.name(), medium, cut))
                        saveFilePath = ut.savePath(defSavePath, (".pdf", ".png"), outDirPath=outDirPath)
                        plt.savefig(saveFilePath, bbox_inches='tight', pad_inches=0.25)
                        plt.close()
                        logging.info("Created {}".format(saveFilePath))

# ----------------------------------------------------------------------
