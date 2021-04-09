import numpy as np


class DriftData:
    def __init__(self, dataPath):
        self.data = np.loadtxt(dataPath)#maybe make sure the path exists and there is a file there?

        #extract the data
        self.localVelXY = (self.data[:,0], self.data[:,1])
        self.angularVel = self.data[:,2]
        self.sideslip = self.data[:,3]
        self.nextWP0 = (self.data[:,4], self.data[:,5])
        self.nextWP1 = (self.data[:,6], self.data[:,7])
        self.nextWP2 = (self.data[:,8], self.data[:,9])
        self.nextWP3 = (self.data[:,10], self.data[:,11])
        self.nextWP4 = (self.data[:,12], self.data[:,13])
        self.rpm = self.data[:,14]
        self.currSteerDir = self.data[:,15]



