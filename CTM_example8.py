import numpy as np
import matplotlib.pyplot as plt
import pyDyFlowNet as dfn

maxV = 1
maxW = 0.25
maxQ = 50
maxDen = 250
cellLen = 1
timeStep = 1

def sendingFlowFunc(den):
    return np.minimum(maxV*den, maxQ)

def receivingFlowFunc(den):
    return np.minimum(maxW*(maxDen-den), maxQ)

def nodeFlowFunc(sendingFlows, receivingFlows):
    return [np.minimum(sendingFlows[0], receivingFlows[0])], [np.minimum(sendingFlows[0], receivingFlows[0])]

# Initialize sources.
sources = [dfn.Source(sourceID="source0", maxSpeed=maxV, sendingFlowFunc=sendingFlowFunc, demandFunc=lambda:0)]

# Initialize 101 cells (initial density from 150 to 0).
numCell = 101
initialDens = [25 for _ in range(numCell)]
for i in [49, 50, 51]:
    initialDens[i] = 250
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
for t in range(32):
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
plt.plot(range(1, 21), np.cumsum(denOutput[0, 41:61]), 'o--')
plt.plot(range(1, 21), np.cumsum(denOutput[8, 41:61]), 'o--')
plt.plot(range(1, 21), np.cumsum(denOutput[16, 41:61]), 'o--')
plt.plot(range(1, 21), np.cumsum(denOutput[24, 41:61]), 'o--')
plt.plot(range(1, 21), np.cumsum(denOutput[32, 41:61]), 'o--')
plt.legend(["Time step 0", "Time step 8", "Time step 16", "Time step 24", "Time step 32"])
plt.ylim([0, 1200])
plt.ylabel("Cumulative vehicle count")
plt.gca().set_xticks(range(1, 21))
plt.xlabel("Cells")
plt.grid()
plt.tight_layout()
plt.savefig("CTM_example8.pdf")