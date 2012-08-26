#!/usr/bin/env python
# a quick script to test things
# example: >>> reload(run) ; run.run()
# 'http://www.physics.nmt.edu/~raymond/software/python_notes/paper004.html'
import matplotlib
matplotlib.use('ps')
from matplotlib import pyplot as plt
from matplotlib import rc
from numpy import arange, floor, ceil
from pylab import *

def rstyle(ax): 
    """Styles an axes to appear like ggplot2
    Must be called after all plot and axis manipulation operations have been carried out (needs to know final tick spacing)
    """
    #set the style of the major and minor grid lines, filled blocks
    ax.grid(True, 'major', color='w', linestyle='-', linewidth=1.4)
    ax.grid(True, 'minor', color='0.92', linestyle='-', linewidth=0.7)
    ax.patch.set_facecolor('0.85')
    ax.set_axisbelow(True)
    
    #set minor tick spacing to 1/2 of the major ticks
    ax.xaxis.set_minor_locator(MultipleLocator( (plt.xticks()[0][1]-plt.xticks()[0][0]) / 2.0 ))
    ax.yaxis.set_minor_locator(MultipleLocator( (plt.yticks()[0][1]-plt.yticks()[0][0]) / 2.0 ))
    
    #remove axis border
    for child in ax.get_children():
        if isinstance(child, matplotlib.spines.Spine):
            child.set_alpha(0)
       
    #restyle the tick lines
    for line in ax.get_xticklines() + ax.get_yticklines():
        line.set_markersize(5)
        line.set_color("gray")
        line.set_markeredgewidth(1.4)
    
    #remove the minor tick lines    
    for line in ax.xaxis.get_ticklines(minor=True) + ax.yaxis.get_ticklines(minor=True):
        line.set_markersize(0)
    
    #only show bottom left ticks, pointing out of axis
    rcParams['xtick.direction'] = 'out'
    rcParams['ytick.direction'] = 'out'
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    
    
    if ax.legend_ <> None:
        lg = ax.legend_
        lg.get_frame().set_linewidth(0)
        lg.get_frame().set_alpha(0.5)

        
def rhist(ax, data, **keywords):
    """Creates a histogram with default style parameters to look like ggplot2
    Is equivalent to calling ax.hist and accepts the same keyword parameters.
    If style parameters are explicitly defined, they will not be overwritten
    """
    
    defaults = {
                'facecolor' : '0.3',
                'edgecolor' : '0.28',
                'linewidth' : '1',
                'bins' : 100
                }
    
    for k, v in defaults.items():
        if k not in keywords: keywords[k] = v
    
    return ax.hist(data, **keywords)
    


def rbox(ax, data, **keywords):
    """Creates a ggplot2 style boxplot, is eqivalent to calling ax.boxplot with the following additions:
    
    Keyword arguments:
    colors -- array-like collection of colours for box fills
    names -- array-like collection of box names which are passed on as tick labels

    """

    bp = ax.boxplot(data)
    pylab.setp(bp['boxes'], color='black')
    pylab.setp(bp['whiskers'], color='black', linestyle = 'solid')
    pylab.setp(bp['fliers'], color='black', alpha = 0.9, marker= 'o', markersize = 3)
    pylab.setp(bp['medians'], color='black')
    
    
    hasColors = 'colors' in keywords
    if hasColors:
        colors = keywords['colors']
        
    if 'names' in keywords:
        ax.tickNames = plt.setp(ax, xticklabels=keywords['names'] )
    
    numBoxes = len(data)
    for i in range(numBoxes):
        box = bp['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
          boxX.append(box.get_xdata()[j])
          boxY.append(box.get_ydata()[j])
        boxCoords = zip(boxX,boxY)
        
        if hasColors:
            boxPolygon = Polygon(boxCoords, facecolor = colors[i % len(colors)])
        else:
            boxPolygon = Polygon(boxCoords, facecolor = '0.95', label = "Test")
        
        
        ax.add_patch(boxPolygon)
    return np


def run():
	gridsize = [[-2.5,3],[-1,4]]
	fig = plt.figure(figsize=(4,6))
	fig.subplots_adjust(left=0.2, right=0.9,
						bottom=0.2, top=0.9,
						wspace=0.2, hspace=0.2)
	
	matplotlib.rcdefaults()

	rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'],'weight':'lighter'})
	rc('lines',linewidth=2, color='black')
	rc('patch',facecolor='white')
	rc('grid',color='grey',linestyle='-', linewidth=0.1)
	rc('xtick.major',pad=8, size=8)
	rc('ytick.major',pad=8, size=8)
	rc('xtick.minor', size=4)
	rc('ytick.minor', size=4)
	# rc('font',size=20)
	# rc('text', usetex=True)
	# rc('ps', fonttype=42)
	# rc('ps',usedistiller=None)
	# rc('ps.distiller',res=6000)
	# rc('text',dvipnghack=True)
	# Axis
	ax = fig.add_subplot(111)
	ax.set_aspect('equal')
	ax.grid(True)
	# ax.autoscale(False)

	# print matplotlib.rcParams.keys()
	# rc('xtick',direction='in', labelsize='small')
	# rc('ytick',direction='in')

	# X Axis
	ax.set_xlabel('X [inch]')
	ax.set_xlim(gridsize[0])

	from matplotlib.ticker import Locator
	class inchLocator(Locator):
		def __init__(self, ndiv=2):
			self.ndiv=2**ndiv
		def __call__(self):
			major = self.axis.get_ticklocs()
			ticks = []
			spacing = 1.0/self.ndiv
			for m in major:
				for div in range(1,self.ndiv):
					ticks.append(m+div*spacing)
			return ticks

	def setTicks(axis, ndiv=4):
		minor = axis.get_minor_ticks()
		spacing = 1.0/ndiv
		ticks = []
		help(minor[0])
		for i,m in enumerate(minor):
			print (i % ndiv)
			# m.set_length()
			# help(m)
			# for div in range(1,ndiv):
				# ticks.append(m+div*spacing)
		return minor


	# major = inchLocator
	# ax.xaxis.set_major_locator(major)
	ndiv=4
	ax.xaxis.set_minor_locator(inchLocator(ndiv))
	ax.xaxis.set_ticks(setTicks(ax.xaxis,ndiv), minor=True)
	# Y Axis
	ax.set_ylabel('Y [inch]')
	ax.set_ylim(gridsize[1])

	x = arange(-10.,10.,1)
	y = x
	ax.plot(x,y, color='k')
	ax.set_adjustable("datalim")
	# rstyle(ax)
	plt.savefig('fig1.ps', dpi=150,format='eps')
	# reload(visualize)
	# reload(image)
	# gfile = '~/Dropbox/Shared/robottown/pcb_design/doubleSided/Mendez.bot.etch_opt.tap'
	# visualize.main(gfile)

# run()