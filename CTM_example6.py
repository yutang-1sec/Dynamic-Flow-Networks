import numpy as np
import matplotlib.pyplot as plt
import pyDyFlowNet as dfn

maxV = 1
maxQ = 50
maxDen = 150
cellLen = 1
timeStep = 1

def sendingFlowFunc(den):
    return np.minimum(maxV*den, maxQ)

def receivingFlowFunc(den):
    return np.minimum(maxV*(maxDen-den), maxQ)

def nodeFlowFunc(sendingFlows, receivingFlows):
    return [np.minimum(sendingFlows[0], receivingFlows[0])], [np.minimum(sendingFlows[0], receivingFlows[0])]

# Initialize sources.
sources = [dfn.Source(sourceID="source0", maxSpeed=maxV, sendingFlowFunc=sendingFlowFunc, demandFunc=lambda:0)]

# Initialize 151 cells (initial density from 150 to 0).
numCell = 151
initialDens = np.linspace(150, 0, 151)
cells = [dfn.Link(linkID=f"cell{i}", initialDen=initialDens[i], maxSpeed=maxV, 
                  sendingFlowFunc=sendingFlowFunc, maxDen=maxDen, receivingFlowFunc=receivingFlowFunc) for i in range(numCell)]

# Initialize sinks.
sinks = [dfn.Sink("sink0")]

# Initialize nodes.
nodes = [dfn.Node(nodeID="node0", incomingLinks=[sources[0]], outgoingLinks=[cells[0]], nodeFlowFunc=nodeFlowFunc)]
for i in range(numCell-1):
    nodes.append(dfn.Node(nodeID=f"node{i+1}", incomingLinks=[cells[i]], outgoingLinks=[cells[i+1]], nodeFlowFunc=nodeFlowFunc))
nodes.append(dfn.Node(nodeID=f"node{numCell}", incomingLinks=[cells[-1]], outgoingLinks=[sinks[0]], nodeFlowFunc=nodeFlowFunc))

# Run.
for t in range(20):
    for s in sources:
        s.updateDemand()
        s.updateSendingFlow(den=s.den)

    for c in cells:
        c.updateSendingFlow(den=c.den)
        c.updateReceivingFlow(den=c.den)

    for s in sinks:
        s.updateReceivingFlow()

    for n in nodes:
        n.getSendingFlows()
        n.getReceivingFlows()
        
        n.updateNodeFlow()

        n.setOutflows()
        n.setInflows()

    for s in sources:
        s.updateSpeed()
        s.updateDensity()

    for c in cells:
        c.updateSpeed()
        c.updateDensity()

    for s in sinks:
        s.updateDensity()

# Show the output.
denOutput = []
for c in cells:
    denOutput.append(c.output["den"])
denOutput = np.array(denOutput).transpose()

plt.figure(figsize=(5, 4))
plt.plot([50, 50], [0, 20], color="red", linestyle="dashed")
plt.plot([100, 100],[0, 20], color="red", linestyle="dashed")
plt.plot([50, 40], [0, 20], color="red", linestyle="dashed")
plt.plot([100, 110], [0, 20], color="red", linestyle="dashed")
plt.legend(["Shock wave"])
plt.imshow(denOutput, aspect="auto", vmin=0, vmax=150)
plt.xlabel("Cells")
plt.ylabel("Time")
cbar=plt.colorbar()
cbar.set_label("Density")
plt.tight_layout()
plt.savefig("CTM_example6.pdf")