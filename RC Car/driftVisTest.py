import random, time
from tornado.ioloop import IOLoop
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from threading import Thread
import asyncio
import numpy as np



from bokeh.plotting import gridplot

############################MAKE SURE A BROWSERWINDOW IS OPEN BEFORE RUNNING THIS CODE,
############################otherwise it will throw a nvrm: cant initialize... error.###


class DriftDataLiveVisualizer():
    #plot_data = []
    #plot_data.append({'x': [time.time()], 'y': [random.random()], 'color': [random.choice(['red', 'blue', 'green'])]})
    #last_data_length = None
    locVelDataX = []
    locVelDataY = []
    angVelData = []
    sideSlipData = []
    nxtWPsData = []
    rpmData = []
    currSteerDirData = []

    throttleData = []
    steeringData = []

    carPosData = []
    WPvisData = []
    WPlineData = []

    time_secs = 0

    #locVelData.append({'x': [random.random()], 'y': [random.random()], 'color': [random.choice(['red', 'blue', 'green'])]})


    def __init__(self, car_measu_data, car_act_data, car_wps_data, car_pos_data, car_wpVis_data, car_orthLinedata):
        #the data lists have to be initialized (BEFORE calling run_server) with a value, otherwise the server will try to plot an empty list and throw an error.
        self.update_car_measurement_data(car_measu_data)
        self.update_car_action_data(car_act_data)
        self.update_car_posWP_data(car_wps_data, car_pos_data, car_wpVis_data, car_orthLinedata)

        thread = Thread(target = self.run_server)
        thread.start()


    def run_server(self):
        asyncio.set_event_loop(asyncio.new_event_loop())#https://github.com/tornadoweb/tornado/issues/2308
        io_loop = IOLoop.current()
        server = Server(applications = {'/RCdrift_live_plotter': Application(FunctionHandler(self.make_document))}, io_loop = io_loop, port = 5001, allow_websocket_origin=["*"])
        server.start()
        server.show('/RCdrift_live_plotter')
        io_loop.start()


    def make_document(self, doc):
        source_locVelX = ColumnDataSource({'x': [], 'y': []})
        source_locVelY = ColumnDataSource({'x': [], 'y': []})
        source_angVel = ColumnDataSource({'x': [], 'y': []})
        source_sideSlip = ColumnDataSource({'x': [], 'y': []})
        source_nxtWPs = ColumnDataSource({'x': [], 'y': []})#({'x0': [], 'y0': []'x1': [], 'y1': [], 'x2': [], 'y2': [], 'x3': [], 'y3': [], 'x4': [], 'y4': []})
        source_rpm = ColumnDataSource({'x': [], 'y': []})
        source_currSteerDir = ColumnDataSource({'x': [], 'y': []})
        source_carPos = ColumnDataSource({'x': [], 'y': [], 'ang': []})
        source_WPsVis = ColumnDataSource({'x': [], 'y': []})
        source_WPline = ColumnDataSource({'orthgLstartx0': [], 'orthgLstarty0': [], 'orthgLendx1': [], 'orthgLendy1': []})

        #fig = figure(title = 'Streaming Circle Plot!', sizing_mode = 'scale_both')
        #fig.line(source = source, x = 'x', y = 'y')


        #create the figure objects
        p_locVel = figure(width=350, plot_height=250, title="Local Velocity")
        p_angVel = figure(width=350, plot_height=250, title="Angular Velocity")
        p_sideSlip = figure(width=350, plot_height=250, title="Sideslip")
        p_nxtWPs = figure(width=350, plot_height=350, title="Next Waypoints")
        p_rpm = figure(width=350, plot_height=250, title="RPM")
        p_currSteerDir = figure(width=350, plot_height=250, title="Current Steer Direction")


        #add the data to the figure objects
        p_locVel.line(source = source_locVelX, x = 'x', y = 'y', line_width=2)
        p_locVel.line(source = source_locVelY, x = 'x', y = 'y', line_width=2, line_color="red")
        p_angVel.line(source = source_angVel, x = 'x', y = 'y', line_width=2)
        p_sideSlip.line(source = source_sideSlip, x = 'x', y = 'y', line_width=2)
        p_nxtWPs.circle(source = source_nxtWPs, x = 'x', y = 'y', size=10)
        p_rpm.line(source = source_rpm, x = 'x', y = 'y', line_width=2)
        p_currSteerDir.line(source = source_currSteerDir, x = 'x', y = 'y', line_width=2)
        p_nxtWPs.rect(source=source_carPos, x='x', y='y', width=0.1, height=0.35, color="#FAB2D6", angle='ang')
        p_nxtWPs.annulus(source=source_WPsVis, x='x', y='y', inner_radius=0.1, outer_radius=0.2, color="red", alpha=0.6)
        p_nxtWPs.segment(source=source_WPline, x0='orthgLstartx0', y0='orthgLstarty0', x1='orthgLendx1', y1='orthgLendy1', color="#F4A582", line_width=3)


        #only send the newest datapoint to the server
        def update():
            #if self.last_data_length is not None and self.last_data_length != len(self.plot_data):
            #source.stream(self.plot_data[-1], rollover=10)
            #self.last_data_length = len(self.plot_data)
            source_locVelX.stream(self.locVelDataX[-1], rollover=100)
            source_locVelY.stream(self.locVelDataY[-1], rollover=100)
            source_angVel.stream(self.angVelData[-1], rollover=100)
            source_sideSlip.stream(self.sideSlipData[-1], rollover=100)
            source_nxtWPs.stream(self.nxtWPsData[-1], rollover=len(self.nxtWPsData[-1]['x']))
            source_rpm.stream(self.rpmData[-1], rollover=100)
            source_currSteerDir.stream(self.currSteerDirData[-1], rollover=100)
            source_carPos.stream(self.carPosData[-1], rollover=1)
            source_WPsVis.stream(self.WPvisData[-1], rollover=len(self.WPvisData[-1]['x']))
            source_WPline.stream(self.WPlineData[-1], rollover=1)

            self.time_secs += 1 

        p = gridplot([[p_locVel, p_angVel, p_sideSlip, p_rpm, p_currSteerDir], [p_nxtWPs]])
        doc.add_root(p)
        doc.add_periodic_callback(update, 100)


    def update_car_measurement_data(self, mdata):
        #self.plot_data[0] = {'x': [time.time()], 'y': [random.random()], 'color': [random.choice(['red', 'blue', 'green'])]}
        self.locVelDataX.append({'x': [self.time_secs], 'y': [mdata[0]]})
        self.locVelDataY.append({'x': [self.time_secs], 'y': [mdata[1]]})
        self.angVelData.append({'x': [self.time_secs], 'y': [mdata[2]]})
        self.sideSlipData.append({'x': [self.time_secs], 'y': [mdata[3]]})
        self.rpmData.append({'x': [self.time_secs], 'y': [mdata[4]]})
        self.currSteerDirData.append({'x': [self.time_secs], 'y': [mdata[5]]})


    def update_car_action_data(self, adata):
        self.throttleData.append({'x': [self.time_secs], 'y': [adata[1]]})
        self.steeringData.append({'x': [self.time_secs], 'y': [adata[0]]})


    def update_car_posWP_data(self, pdata, cdata, vdata, orthLdata):
        self.nxtWPsData.append({'x': pdata[0,:], 'y': pdata[1,:]})
        self.carPosData.append({'x': [cdata[0]], 'y': [cdata[1]], 'ang': [cdata[2]]})
        self.WPvisData.append({'x': vdata[0,:], 'y': vdata[1,:]})
        self.WPlineData.append({'orthgLstartx0': [orthLdata[0].x], 'orthgLstarty0': [orthLdata[0].y], 'orthgLendx1': [orthLdata[1].x], 'orthgLendy1': [orthLdata[1].y]})




#testing
if __name__ == '__main__':
    app = DriftDataLiveVisualizer([3, 1, 0.2, 1, 10, -1], [0.7, -0.3], np.array([[1, 2, 3], [4, 5, 6]]), [2.5, 3.5, np.pi/3])

    while True:
        app.update_car_measurement_data(np.random.rand(6, 1))
        app.update_car_action_data(np.random.rand(2, 1))
        app.update_car_posWP_data(np.array([[1, 2, 3, 5], [4, 5, 6, 6.45]]), [2.5, 3.5, np.pi/2])
        time.sleep(0.1)

