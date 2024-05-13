import numpy as np

def updateDensity(den, inflow, outflow, timeStep, length, maxDen):
    den += (inflow-outflow)*timeStep/length
    return np.minimum(np.maximum(0, den), maxDen)


def updateSpeed(den, outflow, maxSpeed):
    if np.sum(den==0) == 0:
        # The density is greater than zero.
        return outflow / den
    else:
        # If the density equals zero, then the outflow must equal zero.
        outflow = outflow * (den>0)
        
        # To avoid zero divided by zero, we set the speed equal to the maximum value.
        outflow += (den==0)*maxSpeed
        den += (den==0)
        return outflow / den


class Link:
    def __init__(self, linkID, initialDen, maxSpeed, sendingFlowFunc, length=1, timeStep=1, maxDen=np.inf, initialSpeed=None, receivingFlowFunc=lambda:np.inf) -> None:
        self.id = linkID

        self.len = length
        self.timeStep = timeStep

        # Initialize density.
        self.den = initialDen
        # Set maximum density. 
        self.maxDen = maxDen

        # Initialize speed.
        self.speed = maxSpeed if initialSpeed is None else initialSpeed
        # Set maximum speed.       
        self.maxSpeed = maxSpeed

        # Set sending flow function.
        self.sendingFlowFunc = sendingFlowFunc

        # Set receiving flow function.        
        self.receivingFlowFunc = receivingFlowFunc

        self.sendingFlow = None
        self.receivingFlow = None

        self.outflow = None
        self.inflow = None

        # Initialize output.
        self.output = {
            "den": [self.den], 
            "speed": [self.speed], 
            "sendingFlow": [], 
            "receivingFlow": [],
            "outflow": [],
            "inflow": []
        }

    def updateDensity(self):
        self.den = updateDensity(self.den, self.inflow, self.outflow, self.timeStep, self.len, self.maxDen)
        self.output["den"].append(self.den)

    def updateSpeed(self):
        self.speed = updateSpeed(self.den, self.outflow, self.maxSpeed)
        self.output["speed"].append(self.speed)

    def updateSendingFlow(self, **kwargs):
        self.sendingFlow = self.sendingFlowFunc(**kwargs)
        self.output["sendingFlow"].append(self.sendingFlow)

    def updateReceivingFlow(self, **kwargs):
        self.receivingFlow = self.receivingFlowFunc(**kwargs)
        self.output["receivingFlow"].append(self.receivingFlow)

    def updateOutflow(self, outflow):
        self.outflow = outflow
        self.output["outflow"].append(outflow)

    def updateInflow(self, inflow):
        self.inflow = inflow
        self.output["inflow"].append(inflow)


class Source:
    def __init__(self, sourceID, maxSpeed, sendingFlowFunc, demandFunc, length=1, timeStep=1, initialDen=0, initialSpeed=None) -> None:
        self.id = sourceID

        self.len = length
        self.timeStep = timeStep

        # Initialize density.
        self.den = initialDen

        # Initialize speed.
        self.speed = maxSpeed if initialSpeed is None else initialSpeed
        # Set maximum speed.
        self.maxSpeed = maxSpeed

        # Set sending flow function.
        self.sendingFlowFunc = sendingFlowFunc

        # Set demand function.
        self.demandFunc = demandFunc

        self.sendingFlow = None
        
        self.demand = None
        self.outflow = None

        # Initialize output.
        self.output = {
            "den": [self.den], 
            "speed": [self.speed], 
            "sendingFlow": [], 
            "outflow": [],
            "demand": []
        }

    def updateDensity(self):
        self.den = updateDensity(self.den, self.demand, self.outflow, self.timeStep, self.len, np.inf)
        self.output["den"].append(self.den)

    def updateSpeed(self):
        self.speed = updateSpeed(self.den, self.outflow, self.maxSpeed)
        self.output["speed"].append(self.speed)

    def updateSendingFlow(self, **kwargs):
        self.sendingFlow = self.sendingFlowFunc(**kwargs)
        self.output["sendingFlow"].append(self.sendingFlow)

    def updateDemand(self, **kwargs):
        self.demand = self.demandFunc(**kwargs)
        self.output["demand"].append(self.demand)

    def updateOutflow(self, outflow):
        self.outflow = outflow
        self.output["outflow"].append(outflow)

class Sink:
    def __init__(self, sinkID, initialDen=0, length=1, timeStep=1, receivingFlowFunc=lambda:np.inf) -> None:
        self.id = sinkID

        self.len = length
        self.timeStep = timeStep

        # Initialize density.
        self.den = initialDen

        # Set receiving flow function.
        self.receivingFlowFunc = receivingFlowFunc

        self.receivingFlow = None
        self.inflow = None

        # Initialize output.
        self.output = {
            "den": [self.den], 
            "receivingFlow": [],
            "inflow": []
        }

    def updateDensity(self):
        # Outflow equals zero. 
        self.den = updateDensity(self.den, self.inflow, 0, self.timeStep, self.len, np.inf)
        self.output["den"].append(self.den)

    def updateReceivingFlow(self, **kwargs):
        self.receivingFlow = self.receivingFlowFunc(**kwargs)
        self.output["receivingFlow"].append(self.receivingFlow)

    def updateInflow(self, inflow):
        self.inflow = inflow
        self.output["inflow"].append(inflow)


class Node:
    def __init__(self, nodeID, incomingLinks, outgoingLinks, nodeFlowFunc) -> None:
        self.id = nodeID

        self.incomingLinks = incomingLinks
        self.outgoingLinks = outgoingLinks
        
        self.nodeFlowFunc = nodeFlowFunc

        self.sendingFlows = None
        self.receivingFlows = None
        
        self.outflows = None
        self.inflows = None

    def getSendingFlows(self):
        self.sendingFlows = [link.sendingFlow for link in self.incomingLinks]

    def getReceivingFlows(self):
        self.receivingFlows = [link.receivingFlow for link in self.outgoingLinks]

    def setOutflows(self):
        for i, outflow in enumerate(self.outflows):
            self.incomingLinks[i].updateOutflow(outflow)

    def setInflows(self):
        for i, inflow in enumerate(self.inflows):
            self.outgoingLinks[i].updateInflow(inflow)

    def updateNodeFlow(self):
        self.outflows, self.inflows = self.nodeFlowFunc(self.sendingFlows, self.receivingFlows)