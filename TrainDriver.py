# CYPRESS-specific script to drive a (virtual) train around the layout
# Bob Jacobsen 2022

import jmri

import java
import java.awt
import java.awt.event
import javax.swing

# Manual data initialization
#   Map Sensors <-> BLOCKSIZE via names
blockNameToSensorNameDict = {
    # TODO: make automatically from block contents
    "IBIS1":"IS1",
    "IBIS2":"IS2",
    "IBIS3":"IS3",
    "IBIS4":"IS4",
    "IBIS5":"IS5",
    "IBIS6":"IS6",
    "IBIS7":"IS7",
    "IBIS8":"IS8",
    "IBIS9":"IS9",
    "IBIS10":"IS10",
    "IBIS11":"IS11",
    "IBIS12":"IS12",
    "IBIS13":"IS13",
    "IBIS14":"IS14",
    "IBIS15":"IS15",
    "IBIS16":"IS16",
    "IBIS17":"IS17",
    "IBIS18":"IS18",
    "IBIS19":"IS19",
    "IBIS20":"IS20",
    "IBIS21":"IS21",
    "IBIS22":"IS22",
    "IBIS23":"IS23",
    "IBIS24":"IS24",
    "IBIS25":"IS25",
    "IBIS26":"IS26",
    "IBIS27":"IS27",
    "IBIS28":"IS28",
}

# Represent one node of the layout topology
class Topology:
    # Arguments are name strings, converted here.
    #   thisBlock - the block this node represents
    #   nextBlock - next block along the main line
    #   turnout   - name of turnout in block, if any, or None
    #   nextDivergingBlock - name of diverging track, if turnout present and relevant, or None
    #   typeTurnout - one of the Topology constants for connectivity
    #   signals - array of signals at exit or None if none; empty array not supported (TODO)
    def __init__(self, thisBlock, nextBlock, turnout, nextDivergingBlock, typeTurnout, signals) :
        self.thisBlock = blocks.provideBlock(thisBlock)
        self.nextBlock = blocks.provideBlock(nextBlock)
        if (turnout != None) :
            self.turnout = turnouts.provideTurnout(turnout)
        else :
            self.turnout = None
        if (nextDivergingBlock != None) :
            self.nextDivergingBlock = blocks.provideBlock(nextDivergingBlock)
        else :
            self.nextDivergingBlock = None
        self.typeTurnout = typeTurnout
        self.signals = signals
        return
    def __repr__(self):
        return "Topology for "+self.thisBlock.getDisplayName()
    def _str_(self):
        return "Topology for "+self.thisBlock.getDisplayName()+" to "+self.nextBlock.getDisplayName()
    # calculate the next block for the train given turnout position as needed
    # None if no move allowed i.e. due to turnout set against
    def dynamicNext(self) :
        if (self.typeTurnout == Topology.SIMPLE) :
            return self.nextBlock
        if (self.typeTurnout == Topology.TRAILING_MAIN) :
            if (self.turnout.getState() == THROWN) :
                return None
            else :
                return self.nextBlock
        if (self.typeTurnout == Topology.TRAILING_DIVERGING) :
            if (self.turnout.getState() == THROWN) :
                return self.nextBlock
            else :
                return None
        if (self.typeTurnout == Topology.FACING) :
            if (self.turnout.getState() == THROWN) :
                return self.nextDivergingBlock
            else :
                return self.nextBlock
    # true is any of the exit signal heads allow movement
    # (usually there's just one, but there's also the case of double head signals...)
    def anyCleared(self) :
        # special case of no signals
        if (not self.signals) : return True
        for signal in self.signals :
            if (signals.getSignalHead(signal).isCleared() and not signals.getSignalHead(signal).getHeld()) : return True
        return False
    # is it possible for the train in this block to advance?
    def willAdvanceFront(self) :
        if (not self.anyCleared()) :
            return False
        #print ("from "+self.thisBlock.displayName+" to "+str(self.dynamicNext())+" is "+str(occupied(self.dynamicNext())) )
        if (occupied(self.thisBlock) and not occupied(self.dynamicNext())) : return True
        return False
    # advance the front of the train in this block, i.e. move into next block
    def advanceFront(self) :
        #print ("setting "+blockToSensorDict[self.dynamicNext()].getSystemName()+" ACTIVE")
        blockToSensorDict[self.dynamicNext()].setState(ACTIVE)
        return
    # advance the rear of the train in this block, i.e. clear the block
    def advanceRear(self) :
        #print ("setting "+blockToSensorDict[self.dynamicNext()].getSystemName()+" INACTIVE for "+self.thisBlock.getSystemName())
        blockToSensorDict[self.thisBlock].setState(INACTIVE)
        return

Topology.SIMPLE = 0             # straight through block
Topology.FACING = 1             # facing point, with two exits
Topology.TRAILING_MAIN = 2      # entering next block on main line of turnout there
Topology.TRAILING_DIVERGING = 3 # entering next block on diverging leg of turnout there


# create the topology array for this specific layout
topologyNodes = [
    # track 1
    Topology("IBIS1", "IBIS2",  None,       None,   Topology.SIMPLE,            ["IHTr1-Ss03"]),
    Topology("IBIS2", "IBIS3",  None,       None,   Topology.SIMPLE,            ["IHTr1-Sd02-U", "IHTr1-Sd02-L"]),
    Topology("IBIS3", "IBIS4",  "Tr1-T03", "IBIS5", Topology.FACING,            []),
    Topology("IBIS4", "IBIS6",  "Tr1-T04",  None,   Topology.TRAILING_MAIN,     ["IHTr1-Ss04"]),
    Topology("IBIS5", "IBIS6",  "Tr1-T04",  None,   Topology.TRAILING_DIVERGING,["IHTr1-Ss05"]),
    Topology("IBIS6", "IBIS23", None,       None,   Topology.SIMPLE,            []),
    Topology("IBIS23","IBIS9",  None,       None,   Topology.SIMPLE,            ["IHTr1-Ss06"]),
    Topology("IBIS9", "IBIS10", None,       None,   Topology.SIMPLE,            ["IHTr1-Ss07"]),
    Topology("IBIS10","IBIS19", None,       None,   Topology.SIMPLE,            []),
    Topology("IBIS19","IBIS17", None,       None,   Topology.SIMPLE,            ["IHTr1-Sd01-U", "IHTr1-Sd01-L"]),
    Topology("IBIS17","IBIS24", "Tr1-T01","IBIS25", Topology.FACING,            []),
    Topology("IBIS24","IBIS26", "Tr1-T02",  None,   Topology.TRAILING_MAIN,     ["IHTr1-Ss01"]),
    Topology("IBIS26","IBIS18", None,       None,   Topology.SIMPLE,            []),
    Topology("IBIS18","IBIS1",  None,       None,   Topology.SIMPLE,            ["IHTr1-Ss02"]),

    # Track 2
    Topology("IBIS16","IBIS12", None,       None,   Topology.SIMPLE,            ["IHTr2-Ss02"]),
    Topology("IBIS12","IBIS22", None,       None,   Topology.SIMPLE,            ["IHTr2-Ss03"]),
    Topology("IBIS22","IBIS7",  None,       None,   Topology.SIMPLE,            []),
    Topology("IBIS7","IBIS8",   None,       None,   Topology.SIMPLE,            ["IHTr2-Ss04"]),
    Topology("IBIS8","IBIS21",  None,       None,   Topology.SIMPLE,            ["IHTr2-Ss05"]),
    Topology("IBIS21","IBIS28", None,       None,   Topology.SIMPLE,            ["IHTr2-Ss06"]),
    Topology("IBIS28","IBIS20", None,       None,   Topology.SIMPLE,            []),
    Topology("IBIS20","IBIS25", "Tr2-T01",  None,   Topology.TRAILING_MAIN,     ["IHTr2-Sd01-U", "IHTr2-Sd01-L"]),
    Topology("IBIS25","IBIS27", None,       None,   Topology.SIMPLE,            ["IHTr2-Sd02-U", "IHTr2-Sd02-L"]),
    Topology("IBIS27","IBIS11", "Tr2-T02", "IBIS26",Topology.FACING,            []),
    Topology("IBIS11","IBIS16", None,       None,   Topology.SIMPLE,            ["IHTr2-Ss01"]),
]

# Create additional data structures
blockToSensorDict = {}
for key in blockNameToSensorNameDict :
    blockToSensorDict[blocks.provideBlock(key)] = sensors.provideSensor(blockNameToSensorNameDict[key])
sensorToBlockDict = {}
for key in blockToSensorDict :
    sensorToBlockDict[blockToSensorDict[key]] = key

# debug printout
#print (blockToSensorDict)
#print (sensorToBlockDict)
#print (topologyNodes)
#print "Setup done"

# set up frame with initialization buttons
# define listener classes to handle each button
class ClearButtonHandler(java.awt.event.ActionListener) :
    def actionPerformed (self, event) :
        # clear blocks
        for key in blockToSensorDict :
            key.setValue(None)
        # clear sensors
        for key in sensorToBlockDict :
            key.setState(INACTIVE)
class StartTrack1ButtonHandler(java.awt.event.ActionListener) :
    def actionPerformed (self, event) :
            sensors.getSensor(blockNameToSensorNameDict["IBIS1"]).setState(ACTIVE)
            blocks.getBlock("IBIS1").setValue("Train 1")
class StartTrack2ButtonHandler(java.awt.event.ActionListener) :
    def actionPerformed (self, event) :
            sensors.getSensor(blockNameToSensorNameDict["IBIS16"]).setState(ACTIVE)
            blocks.getBlock("IBIS16").setValue("Train 2")
class StepTrainsButtonHandler(java.awt.event.ActionListener) :
    def actionPerformed (self, event) :
            stepTrains()
# create a frame to hold the buttons, put buttons in it, and display
f = javax.swing.JFrame("Autorun Control")
f.setLayout(java.awt.FlowLayout())
#
b = javax.swing.JButton("Clear Blocks")
h = ClearButtonHandler()
h.name = "Clear Blocks"
b.addActionListener(h)
f.contentPane.add(b)
#
b = javax.swing.JButton("Start Track 1")
h = StartTrack1ButtonHandler()
h.name = "Start Track 1"
b.addActionListener(h)
f.contentPane.add(b)
#
b = javax.swing.JButton("Start Track 2")
h = StartTrack2ButtonHandler()
h.name = "Start Track 2"
b.addActionListener(h)
f.contentPane.add(b)
#
b = javax.swing.JButton("Step Trains")
h = StepTrainsButtonHandler()
h.name = "Step Trains"
b.addActionListener(h)
f.contentPane.add(b)
#
runCheckBox = javax.swing.JCheckBox("Run")
f.contentPane.add(runCheckBox)
#
f.pack()
f.show()

# Service routine for checking whether a block is occupied
def occupied(block) :
    if (block == None) : return False
    return not (block.getValue() == None or block.getValue() == "")

# Method for moving all trains forward one step.
# Multiple phases to avoid trains stepping on each other:
#  1) Find all trains that can move into a next block
#  2) Move all those
#  3) Find the block of the back end of all trains that can move
#  4) Move those back ends
def stepTrains() :
    # extend front of trains
    # 1) make a list of those to move
    moveNodes = []
    moveTrains = []
    for node in topologyNodes :
        if (node.willAdvanceFront()) :
            moveNodes.append(node)
    # 2) move them
    for node in moveNodes :
        train = node.thisBlock.getValue()
        if (not train in moveTrains) : moveTrains.append(train)
        node.advanceFront()

    # catch up rear of train
    # 3) find rear block of moved trains
    moveNodes = []
    for train in moveTrains :
        #print("scanning for "+str(train))
        # find rear of train
        for node in topologyNodes :
            if (node.thisBlock.getValue() == train) :
                #print ("   found train \""+str(train)+"\" in \""+str(node)+"\"")
                # node contains train, but not last if also in prior
                prior = findPrior(node, train)
                if (prior == None) :
                    # no prior, this is last
                    moveNodes.append(node)
                    break
                else :
                    # there is a prior, check it
                    if (prior.thisBlock.getValue() != train) :
                       moveNodes.append(node)
                       break
    # 4) advance the rear blocks
    for node in moveNodes :
        node.advanceRear()

# Service routine to find the prior block to this one
def findPrior(node, train) :
    # node contains train, but not last if also in prior
    for prior in topologyNodes : #scan for prior
        #print("      check prior \""+str(prior)+"\" with next \""+str(prior.dynamicNext())+"\"")
        if (prior.dynamicNext() == node.thisBlock) :
            #print ("         found prior "+str(prior)+" with train "+str(prior.thisBlock.getValue()))
            return prior
    # did not find one, return None

# Start a thread to do the auto-run if box checked
class AutoRun(jmri.jmrit.automat.AbstractAutomaton) :
    def handle(self) : # this loops around until stopped
        if (runCheckBox.isSelected()) :
            stepTrains()
        self.waitMsec(2000)
        return True
AutoRun().start()
