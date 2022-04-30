# Example of driving a signal
#
# It listens for changes to sensor(s) and the next signal(s)
# and then recalculates a signal aspect based on the values
#
# Author: Bob Jacobsen, copyright 2004, 2022

import jarray
import jmri

class SignalSimpleTrack(jmri.jmrit.automat.Siglet) :
    # `defineIO()` is called exactly once at the beginning, and is
    # required to load the "inputs" array with the turnouts, sensors
    # and signal heads that are used. Any changes in these will result
    # in setOutput being called to recalculate the result.
    #
    # Other implementations will require different ways to make sure that
    # setOutput is invoked whenever inputs change
    #
    def defineIO(self):

        # Create a single list of items to pay attention to
        # Note that the output signal should _not_ in included as an input.
        payAttentionTo = []
        payAttentionTo.extend(self.sensors)
        payAttentionTo.extend(self.nextSignals)
        for item in payAttentionTo:
            print (" - ", item)

        # Register the inputs so setOutput will be called when needed.
        self.setInputs(jarray.array(payAttentionTo, jmri.NamedBean))

        return

    # `setOutput` is called when one of the inputs changes, and is
    # responsible for setting the correct output signal appearance
    #
    # This one handles straight track without turnouts.
    def setOutput(self):
        # decide appearance based on next signal
        # approach next signal if it's all RED
        newAppearence = YELLOW
        for nextSignal in self.nextSignals :
            # (not handling flashing appearances yet)
            if (nextSignal.appearance == GREEN or nextSignal.appearance == YELLOW ) :
                newAppearence = GREEN

        # override to Stop if track is not clear to next signal
        for sensor in self.sensors :
            if (sensor.knownState == ACTIVE) : newAppearence = RED

        # set the signal aspect to the new value
        self.thisSignal.appearance = newAppearence;

        # optionally, print the value for diagnostic purposes
        print self.thisSignal, "output set to ", self.thisSignal.appearance

        return

# end of class definition

# create one of these for the leftmost outer track signal
tr1_ss03 = SignalSimpleTrack()
# configure it with related objects
tr1_ss03.thisSignal = signals.getSignalHead("IHTr1-Ss02")
tr1_ss03.nextSignals = [signals.getSignalHead("IHTr1-Ss03")]  # more than one allowed
tr1_ss03.sensors = [sensors.getSensor("IS1")]
# and start it running
tr1_ss03.start()

# create one for first leftmost innner track signal
tr2_ss01 = SignalSimpleTrack()
tr2_ss01.thisSignal = signals.getSignalHead("IHTr2-Ss01")
tr2_ss01.nextSignals = [signals.getSignalHead("IHTr2-Ss02")]  # more than one allowed
tr2_ss01.sensors = [sensors.getSensor("IS16")]
tr2_ss01.start()

