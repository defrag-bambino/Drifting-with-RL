from drift_data_reader import DriftData
from bokeh.plotting import show, figure, gridplot
from bokeh.palettes import Paired as palette
import itertools 
import numpy as np


data_sources = ['obs_data_sim2.txt', 'obs_data_rc.txt']



#create the figure objects
p_locVel = figure(width=350, plot_height=250, title="Local Velocity")
p_angVel = figure(width=350, plot_height=250, title="Angular Velocity")
p_sideSlip = figure(width=350, plot_height=250, title="Sideslip")
p_nxtWP0 = figure(width=350, plot_height=250, title="Next Waypoint 0")
p_nxtWP1 = figure(width=350, plot_height=250, title="Next Waypoint 1")
p_nxtWP2 = figure(width=350, plot_height=250, title="Next Waypoint 2")
p_nxtWP3 = figure(width=350, plot_height=250, title="Next Waypoint 3")
p_nxtWP4 = figure(width=350, plot_height=250, title="Next Waypoint 4")
p_rpm = figure(width=350, plot_height=250, title="RPM")
p_currSteerDir = figure(width=350, plot_height=250, title="Current Steer Direction")

p_legend = figure(width=300, plot_height=200, title="Legend")



# create a color iterator
colors = itertools.cycle(palette[10])

#add data to them
for data_source in data_sources:
    #load the data from file
    dData = DriftData(data_source)
    X = np.arange(dData.data.shape[0])
    color1=next(colors)
    color2=next(colors)

    #add the data to the figure objects
    p_locVel.line(y=dData.localVelXY[0], x=X, line_width=2, color=color1)
    p_locVel.line(y=dData.localVelXY[1], x=X, line_width=2, color=color2)

    p_angVel.line(y=dData.angularVel, x=X, line_width=2, color=color1)

    p_sideSlip.line(y=dData.sideslip, x=X, line_width=2, color=color1)

    p_nxtWP0.line(y=dData.nextWP0[0], x=X, line_width=2, color=color1)
    p_nxtWP0.line(y=dData.nextWP0[1], x=X, line_width=2, color=color2)

    p_nxtWP1.line(y=dData.nextWP1[0], x=X, line_width=2, color=color1)
    p_nxtWP1.line(y=dData.nextWP1[1], x=X, line_width=2, color=color2)

    p_nxtWP2.line(y=dData.nextWP2[0], x=X, line_width=2, color=color1)
    p_nxtWP2.line(y=dData.nextWP2[1], x=X, line_width=2, color=color2)

    p_nxtWP3.line(y=dData.nextWP3[0], x=X, line_width=2, color=color1)
    p_nxtWP3.line(y=dData.nextWP3[1], x=X, line_width=2, color=color2)

    p_nxtWP4.line(y=dData.nextWP4[0], x=X, line_width=2, color=color1)
    p_nxtWP4.line(y=dData.nextWP4[1], x=X, line_width=2, color=color2)

    p_rpm.line(y=dData.rpm, x=X, line_width=2, color=color1)

    p_currSteerDir.line(y=dData.currSteerDir, x=X, line_width=2, color=color1)

    p_legend.circle(x=[], y=[], legend_label= "X " + data_source, color=color1)
    p_legend.circle(x=[], y=[], legend_label= "Y " + data_source, color=color2)



# put all the plots in a grid layout
p = gridplot([[p_locVel, p_angVel, p_sideSlip, p_rpm, p_currSteerDir], [p_nxtWP0,p_nxtWP1, p_nxtWP2, p_nxtWP3, p_nxtWP4], [p_legend]])

# show the results
show(p)
