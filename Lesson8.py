# Using an Arduino with Python LESSON 8: Live Thermometer 3D Visual Using DHT11.
# https://www.youtube.com/watch?v=xgzbRYzQWPE
# https://toptechboy.com/using-an-arduino-with-python-lesson-8-live-thermometer-3d-visual-using-dht11/

# Internet References:
# https://www.glowscript.org/docs/VPythonDocs/index.html

import time
import serial
from vpython import *
import numpy as np

# vPython refresh rate.
vPythonRefreshRate = 100
# Helper Scale Axis toggle.
showAxis = False
# Test the meters with pseudo random data.
pseudoDataMode = False
pseudoDataCounter = 0 # Used to update some meters more slowly.

# A place on which to put our things...
canvas(title = "<b><i>Arduino with Python - Real World Measurements Visualised!</i></b>", background = color.cyan, width = 800, height = 600)

# Axis for helping with meter design and layout.
if showAxis:
    # An origin axis.
    arrow(color = color.blue, round = True, pos = vector(-0.5, 0, 0), axis = vector(1, 0, 0), shaftwidth = 0.02) # X axis.
    arrow(color = color.blue, round = True, pos = vector(0, -0.5, 0), axis = vector(0, 1, 0), shaftwidth = 0.02) # Y axis.
    arrow(color = color.blue, round = True, pos = vector(0, 0, -0.5), axis = vector(0, 0, 1), shaftwidth = 0.02) # Z axis.
    # An Z offest axis.
    for graduation in range(6): # X axis.
        arrow(color = color.magenta, round = True, pos = vector(graduation / 2, 0, 0.25), axis = vector(0.5, 0, 0), shaftwidth = 0.02)
        arrow(color = color.magenta, round = True, pos = vector(-graduation / 2, 0, 0.25), axis = vector(-0.5, 0, 0), shaftwidth = 0.02)
    for graduation in range(4): # Y axis.
        arrow(color = color.magenta, round = True, pos = vector(0, graduation / 2, 0.25), axis = vector(0, 0.5, 0), shaftwidth = 0.02)
        arrow(color = color.magenta, round = True, pos = vector(0, -graduation / 2, 0.25), axis = vector(0, -0.5, 0), shaftwidth = 0.02)
    for graduation in range(2): # Z axis.
        arrow(color = color.magenta, round = True, pos = vector(0, 0, graduation / 2), axis = vector(0, 0, 0.5), shaftwidth = 0.02)
        arrow(color = color.magenta, round = True, pos = vector(0, 0, -graduation / 2), axis = vector(0, 0, -0.5), shaftwidth = 0.02)

# Return some pseudo random data for meter testing.
def pseudoData():
    time.sleep(0.1) # Not too fast...
    pot1Value = int(1023 * np.random.rand())
    tDHT11 = (70 * np.random.rand() - 10.0)
    hDHT11 = (100 * np.random.rand())
    tDHT22 = (70 * np.random.rand() - 10.0)
    hDHT22 = (100 * np.random.rand())
    return(pot1Value, tDHT11, hDHT11, tDHT22, hDHT22)

# A bag of small screws for us to draw exactly where we like.
def drawScrew(sPos = vector(0, 0, 0)):
    cylinder(color = color.black, opacity = 1, pos = vector(0, 0, 0.05) + sPos, axis = vector(0, 0, 0.04), radius = 0.06) # Head.
    cylinder(color = color.black, opacity = 1, pos = vector(0, 0, 0) + sPos, axis = vector(0, 0, 0.05), radius = 0.03) # Shaft.
    cone(color = color.black, opacity = 1, pos = vector(0, 0, 0) + sPos, axis = vector(0, 0, -0.25), radius = 0.03) # Thread.
    slotAngle = np.random.rand() * np.pi / 2 # An angle between 0 and 90 degrees.
    screwCross1 = box(color = vector(0.8, 0.8, 0.8), opacity = 1, pos = vector(0, 0, 0.0801) + sPos, size = vector(0.1, 0.02, 0.02)) # Cross pt1.
    screwCross1.rotate(angle = slotAngle, axis = vector(0, 0, 1)) # Randomly rotate this part of the cross.
    screwCross2 = box(color = vector(0.8, 0.8, 0.8), opacity = 1, pos = vector(0, 0, 0.0801) + sPos, size = vector(0.1, 0.02, 0.02)) # Cross pt2.
    screwCross2.rotate(angle = slotAngle + np.pi / 2, axis = vector(0, 0, 1)) # Add 90 degrees for the other part of the cross.

# Meter Type 1 - A rectangluar style meter with a curved scale and a needle.
class meterType1:
    def __init__(self, mt1Pos = vector(0, 0, 0), mt1Color = color.red, mt1ScaleMin = 0, mt1ScaleMax = 5, mt1Label = "", mt1Units = ""):
        self.mt1Pos = mt1Pos
        self.mt1Color = mt1Color
        self.mt1ScaleMin = int(mt1ScaleMin)
        self.mt1ScaleMax = int(mt1ScaleMax)
        self.mt1ScaleRange = mt1ScaleMax - mt1ScaleMin
        self.mt1Label = mt1Label
        self.mt1Units = mt1Units
        # Draw the meter...
        box(color = color.white, opacity = 1, size = vector(2.25, 1.5, 0.1), pos = vector(0, 0, 0) + self.mt1Pos) # Draw the meter box.
        # Draw the meter needle and set it to the 0 position.
        self.meterNeedle = arrow(length = 1, shaftwidth = 0.02, color = self.mt1Color, round = True, pos = vector(0, -0.65, 0.1) + self.mt1Pos, axis = vector(np.cos(5 * np.pi / 6), np.sin(5 * np.pi / 6), 0))
        cylinder(color = self.mt1Color, opacity = 1, radius = 0.05, pos = vector(0, -0.65, 0.05) + self.mt1Pos, axis = vector(0, 0, 0.1))
        cylinder(color = color.gray(0.5), opacity = 1, radius = 0.2, pos = vector(0, -0.5, 0.05) + self.mt1Pos, axis = vector(0, 0, 0.01))
        # Draw the meter scale major marks.
        for unitCounter, theta in zip(range(self.mt1ScaleMin, self.mt1ScaleMax + 1), np.linspace(5 * np.pi / 6, np.pi / 6, self.mt1ScaleRange + 1)):
            majorUnit = text(text = str(unitCounter), color = self.mt1Color, opacity = 1, align = "center", height = 0.1, pos = vector(1.1 * np.cos(theta), 1.1 * np.sin(theta) - 0.65, 0.095) + self.mt1Pos)
            majorUnit.rotate(angle = theta - np.pi / 2, axis = vector(0, 0, 1))
            box(color = color.black, pos = vector(np.cos(theta), np.sin(theta) - 0.65, 0.08) + self.mt1Pos, size = vector(0.1, 0.02, 0.02), axis = vector(np.cos(theta), np.sin(theta), 0))
        # Draw the meter scale minor marks.
        for unitCounter, theta in zip(range(self.mt1ScaleMin * 10, (self.mt1ScaleMax * 10) + 1), np.linspace(5 * np.pi / 6, np.pi / 6, (self.mt1ScaleRange * 10) + 1)):
            if unitCounter % 5 == 0 and unitCounter % 10 != 0: # Draw the minor unit midway between the major marks.
                minorUnit = text(text = "5", color = self.mt1Color, opacity = 1, align = "center", height = 0.05, pos = vector(1.05 * np.cos(theta), 1.05 * np.sin(theta) - 0.65, 0.095) + self.mt1Pos)
                minorUnit.rotate(angle = theta - np.pi / 2, axis = vector(0, 0, 1))
            box(color = color.black, pos = vector(np.cos(theta), np.sin(theta) - 0.65, 0.08) + self.mt1Pos, size = vector(0.05, 0.01, 0.01), axis = vector(np.cos(theta), np.sin(theta), 0))
        # Meter Label and Units.
        text(text = self.mt1Label, color = self.mt1Color, opacity = 1, align = "center", height = 0.1, pos = vector(0, 0.6, 0.1) + self.mt1Pos, axis = vector(1, 0, 0))
        text(text = self.mt1Units, color = self.mt1Color, opacity = 1, align = "center", height = 0.115, pos = vector(0, 0, 0.1) + self.mt1Pos, axis = vector(1, 0, 0))
        # Add the raw reading too - this is initially not visible as the value may not be provided in future updates.
        self.rawValue = label(text = "0000", visible = False, color = self.mt1Color, height = 10, opacity = 0, box = False, pos = vector(-0.75, 0.6, 0.1) + self.mt1Pos)
        # Add the digital reading too.
        self.digitalValue = label(text = "0.00V", visible = True, color = self.mt1Color, height = 10, opacity = 0, box = False, pos = vector(0.75, 0.6, 0.1) + self.mt1Pos)
        # Corner screws.
        drawScrew(vector(-1.045, 0.67, -0.03) + self.mt1Pos)  # Top Left corner.
        drawScrew(vector(1.045, 0.67, -0.03) + self.mt1Pos)   # Top Right corner.
        drawScrew(vector(-1.045, -0.67, -0.03) + self.mt1Pos) # Bottom Left corner.
        drawScrew(vector(1.045, -0.67, -0.03) + self.mt1Pos)  # Bottom Right corner.
        # Lets put a mostly transparent glass cover over the meter.
        box(color = color.white, opacity = 0.25, size = vector(2.25, 1.5, 0.25), pos = vector(0, 0, 0.15) + self.mt1Pos)
        # At this point we have no data to drive the meter.
        self.DataWarning = text(text = "-No Data-", color = self.mt1Color, opacity = 1, align = "center", height = 0.125, pos = vector(0, -0.25, 0.2) + self.mt1Pos, axis = vector(1, 0, 0))
    def update(self, mt1Value = "nan", mt1RawValue = "-1"):
        if mt1Value != "nan":
            # Clip the meter value if it is out of range.
            if mt1Value < self.mt1ScaleMin:
                self.mt1Value = self.mt1ScaleMin
            elif mt1Value > self.mt1ScaleMax:
                self.mt1Value = self.mt1ScaleMax
            else:
                self.mt1Value = mt1Value
            if mt1RawValue != "-1":
                self.mt1RawValue = mt1RawValue
                self.rawValue.visible = True
            else:
                self.rawValue.visible = False
            # Turn off the data warning.
            self.DataWarning.opacity = 0
            # Print the raw potentiometer value.
            self.rawValue.text = str("<i>%04d</i>" % self.mt1RawValue)
            # Print the digital value.
            self.digitalValue.text = str("%1.2f" % self.mt1Value) + "V"
            # Use the value to set the angle of meter needle... explanation...
            #   0V is 5pi/6 rads, 5V is pi/6 rads, thus the needle movement range is 4pi/6 rads.
            #   The value range is ScaleMin -> ScaleMax, or ScaleRange, so needle angle is the (needle range * value/max) ratio.
            #       = 4pi/6 * (Value - ScaleMin) / ScaleRange rads.
            #   Thus, the needle position is 5pi/6 - (4pi/6 * (Value - ScaleMin) / ScaleRange) rads.
            # e.g. ScaleMin = -5, ScaleMax = +5, ScaleRange = 10 => needle position is 5pi/6 - (4pi/6 * (Value - -5) / 10) rads
            theta  = (5 * np.pi / 6) - (4 * np.pi / 6 * ((self.mt1Value - self.mt1ScaleMin) / self.mt1ScaleRange))
            self.meterNeedle.axis = vector(np.cos(theta), np.sin(theta), 0)
        else:
            # Turn on the data warning.
            self.DataWarning.opacity = 1

# Meter Type 2 - A circular style meter with a scale and a curved 100 segment bar.
class meterType2:
    def __init__(self, mt2Pos = vector(0, 0, 0), mt2Color = color.blue, mt2ScaleMin = 0, mt2ScaleMax = 100, mt2Label = "", mt2Units = ""):
        self.mt2Pos = mt2Pos
        self.mt2Color = mt2Color
        self.mt2ScaleMin = int(mt2ScaleMin)
        self.mt2ScaleMax = int(mt2ScaleMax)
        self.mt2ScaleRange = mt2ScaleMax - mt2ScaleMin
        self.mt2Label = mt2Label
        self.mt2Units = mt2Units
        # Draw the meter...
        cylinder(color = color.white, opacity = 1, radius = 0.85, pos = vector(0, 0, -0.05) + self.mt2Pos, axis = vector(0, 0, 0.1)) # Draw the meter dial.
        # Draw the meter segments and set them to "off" status.
        self.meterSegments = [] # A list in which to put all the meter segments for later referance and update.
        for segmentCounter, theta in zip(range(self.mt2ScaleRange + 1), np.linspace(8 * np.pi / 6, np.pi / 6, self.mt2ScaleRange + 1)):
            # Box segments.
            self.meterSegments.append(box(color = color.white, opacity = segmentCounter / self.mt2ScaleRange, size = vector(0.15, 0.025, 0.02), pos = vector(0.55 * np.cos(theta), 0.55 * np.sin(theta), 0.095) + self.mt2Pos, axis = vector(np.cos(theta - np.pi), np.sin(theta - np.pi), 0)))
            # Cone segments - an option that was considered.
            # self.meterSegments.append(cone(color = color.white, opacity = segmentCounter / self.mt2ScaleRange, size = vector(0.175, 0.025, 0.02), pos = vector(0.625 * np.cos(theta), 0.625 * np.sin(theta), 0.095) + self.mt2Pos, axis = vector(np.cos(theta - np.pi), np.sin(theta - np.pi), 0)))
        # Draw the meter scale major marks.
        for unitCounter, theta in zip(range(self.mt2ScaleRange + 1), np.linspace(8 * np.pi / 6, np.pi / 6, self.mt2ScaleRange + 1)):
            if unitCounter % 10 ==0:
                majorUnit = text(text = str(unitCounter), color = self.mt2Color, opacity = 1, align = "center", height = 0.065, pos = vector(0.75 * np.cos(theta), 0.75 * np.sin(theta), 0.095) + self.mt2Pos)
                majorUnit.rotate(angle = theta - np.pi / 2, axis = vector(0, 0, 1))
                box(color = color.black, pos = vector(0.685 * np.cos(theta), 0.685 * np.sin(theta), 0.095) + self.mt2Pos, size = vector(0.1, 0.02, 0.02), axis = vector(np.cos(theta), np.sin(theta), 0))
        # Draw the meter scale minor marks.
        for unitCounter, theta in zip(range(101), np.linspace(8 * np.pi / 6, np.pi / 6, 101)):
            if unitCounter % 5 == 0 and unitCounter % 10 != 0: # Draw the minor unit midway between the major marks.
                minorUnit = text(text = "5", color = self.mt2Color, opacity = 1, align = "center", height = 0.05, pos = vector(0.72 * np.cos(theta), 0.72 * np.sin(theta), 0.095) + self.mt2Pos)
                minorUnit.rotate(angle = theta - np.pi / 2, axis = vector(0, 0, 1))
            box(color = color.black, pos = vector(0.685 * np.cos(theta), 0.685 * np.sin(theta), 0.095) + self.mt2Pos, size = vector(0.05, 0.01, 0.01), axis = vector(np.cos(theta), np.sin(theta), 0))
        # Meter Label and Units.
        text(text = self.mt2Label, color = self.mt2Color, opacity = 1, align = "center", height = 0.1, pos = vector(0, 0.2, 0.1) + self.mt2Pos, axis = vector(1, 0, 0))
        text(text = self.mt2Units, color = self.mt2Color, opacity = 1, align = "center", height = 0.115, pos = vector(0, -0.3, 0.1) + self.mt2Pos, axis = vector(1, 0, 0))
        # Add the raw digital reading too.
        self.rawValue = label(text = "00.0", color = self.mt2Color, height = 10, opacity = 0, box = False, pos = vector(0.5, 0, 0.1) + self.mt2Pos)
        # Center screw.
        drawScrew(vector(0, 0, -0.03) + self.mt2Pos)
        # Lets put a mostly transparent glass cover over the meter.
        cylinder(color = color.white, opacity = 0.25, radius = 0.85, pos = vector(0, 0, -0.05) + self.mt2Pos, axis = vector(0, 0, 0.25))
        # At this point we have no data to drive the meter.
        self.DataWarning = text(text = "-No Data-", color = self.mt2Color, opacity = 1, align = "center", height = 0.125, pos = vector(0, -0.5, 0.2) + self.mt2Pos, axis = vector(1, 0, 0))
    def update(self, mt2Value = 0):
        # If we have valid data.
        if mt2Value != "nan":
            # Clip the meter value if it is out of range.
            if mt2Value < self.mt2ScaleMin:
                self.mt2Value = self.mt2ScaleMin
            elif mt2Value > self.mt2ScaleMax:
                self.mt2Value = self.mt2ScaleMax
            else:
                self.mt2Value = mt2Value
            # Turn off the data warning.
            self.DataWarning.opacity = 0
            # Print the raw digital sensor value.
            self.rawValue.text = str("<i>%2.1f</i>" % self.mt2Value)
            #Light up the correct meter segments.
            meterSegmentsOn = int(self.mt2Value)
            for meterSegment in range(self.mt2ScaleMin, meterSegmentsOn, 1):
                self.meterSegments[meterSegment + 1].color = self.mt2Color
                self.meterSegments[meterSegment + 1].opacity = 1
            self.meterSegments[meterSegmentsOn + 1].color = self.mt2Color
            self.meterSegments[meterSegmentsOn + 1].opacity = self.mt2Value - meterSegmentsOn
            for meterSegment in range(meterSegmentsOn + 1, self.mt2ScaleMax, 1):
                self.meterSegments[meterSegment + 1].color = color.white
                self.meterSegments[meterSegment + 1].opacity = meterSegment / 100
        else:
            # Turn on the data warning.
            self.DataWarning.opacity = 1

# Meter Type 3 - A thermometer style meter with a scale and rising column.
class meterType3:
    def __init__(self, mt3Pos = vector(0, 0, 0), mt3Color = color.red, mt3ScaleMin = 0.0, mt3ScaleMax = 100.0, mt3Label = "", mt3Units = ""):
        self.mt3Pos = mt3Pos
        self.mt3Color = mt3Color
        self.mt3ScaleMin = mt3ScaleMin
        self.mt3ScaleMax = mt3ScaleMax
        self.mt3Range = mt3ScaleMax - mt3ScaleMin
        self.mt3Label = mt3Label
        self.mt3Units = mt3Units
        # Draw the meter...
        box(color = color.white, opacity = 1, size = vector(0.75, 1.75, 0.1), pos = vector(0, 0, 0) + self.mt3Pos) # Draw the meter box.
        sphere(color = self.mt3Color, radius = 0.1, pos = vector(0, -0.65, 0.15) + self.mt3Pos)
        cylinder(color = color.gray(0.5), opacity = 1, pos = vector(0, -0.65, 0.15) + self.mt3Pos, axis = vector(0, 1.15, 0), radius = 0.049)
        sphere(color = color.gray(0.5), opacity = 1, radius = 0.049, pos = vector(0, 0.5, 0.15) + self.mt3Pos)
        self.measurement = cylinder(color = self.mt3Color, pos = vector(0, -.65, 0.15) + self.mt3Pos, axis = vector(0, 0.15, 0), radius = 0.05)
        for unitCounter, tick in zip(np.linspace(self.mt3ScaleMin, self.mt3ScaleMax, 11), np.linspace(0, 1, 11)):
            text(text = str(unitCounter), color = self.mt3Color, align = "right", height = 0.05, pos = vector(-0.15, -0.6725 + 0.15 + tick, 0.15) + self.mt3Pos)
            box(color = color.black, pos = vector(-0.1, -0.65 + 0.15 + tick, 0.15) + self.mt3Pos, size = vector(0.05, 0.01, 0.01), axis = vector(1, 0, 0))
        for tick in np.linspace(0, 1, 51):
            box(color = color.black, pos = vector(-0.1, -0.65 + 0.15 + tick, 0.15) + self.mt3Pos, size = vector(0.025, 0.005, 0.005), axis = vector(1, 0, 0))
        text(text = self.mt3Label, color = self.mt3Color, opacity = 1, align = "center", height = 0.075, pos = vector(0, 0.6, 0.15) + self.mt3Pos, axis = vector(1, 0, 0))
        text(text = self.mt3Units, color = self.mt3Color, opacity = 1, align = "left", height = 0.095, pos = vector(0.125, -0.685, 0.15) + self.mt3Pos, axis = vector(1, 0, 0))
        # Add the raw reading too.
        self.rawValue = label(text = "00.0", color = self.mt3Color, height = 10, opacity = 0, box = False, pos = vector(0, -0.82, 0.1) + self.mt3Pos)
        # Corner screws.
        drawScrew(vector(-0.3, 0.8, -0.03) + self.mt3Pos)  # Top Left corner.
        drawScrew(vector(0.3, 0.8, -0.03) + self.mt3Pos)   # Top Right corner.
        drawScrew(vector(-0.3, -0.8, -0.03) + self.mt3Pos) # Bottom Left corner.
        drawScrew(vector(0.3, -0.8, -0.03) + self.mt3Pos)  # Bottom Right corner.
        # Lets put a mostly transparent glass cover over the meter.
        box(color = color.white, opacity = 0.25, size = vector(0.75, 1.75, 0.32), pos = vector(0, 0, 0.1) + self.mt3Pos)
        # At this point we have no data to drive the meter.
        self.DataWarning = text(text = "-No Data-", color = self.mt3Color, opacity = 1, align = "center", height = 0.125, pos = vector(0, 0, 0.2) + self.mt3Pos, axis = vector(1, 0, 0))
    def update(self, mt3Value = 0):
        # If we have valid data.
        if mt3Value != "nan":
            # Clip the meter value if it is out of range.
            if mt3Value < self.mt3ScaleMin:
                self.mt3Value = self.mt3ScaleMin
            elif mt3Value > self.mt3ScaleMax:
                self.mt3Value = self.mt3ScaleMax
            else:
                self.mt3Value = mt3Value
            # Turn off the data warning.
            self.DataWarning.opacity = 0
            # Print the raw digital sensor value.
            self.rawValue.text = str("<i>%2.1f</i>" % self.mt3Value)
            # Update the meter reading - basically converting the measurement to a ratio as the whole column is length 1.
            self.measurement.axis = vector(0, 0.15 + ((self.mt3Value - self.mt3ScaleMin)  / self.mt3Range), 0)
        else:
            # Turn on the data warning.
            self.DataWarning.opacity = 1

# Lets draw some meters.
voltageMeter1  = meterType1(vector(0, 0.675, -0.1), color.red, 0, 5, "Potentiometer 1", "V")
thermoMeter1   = meterType3(vector(-2.5, 0.75, -0.1), color.red, -10, 60, "DHT11 Temp", u"\N{DEGREE SIGN}C") # Using UTF8 to get a degree symbol.
humidityMeter1 = meterType2(vector(-2.25, -1.25, -0.1), color.blue, 0, 100, "DHT11 Hum", "%")
thermoMeter2   = meterType3(vector(2.5, 0.75, -0.1), color.red, -10, 60, "DHT22 Temp", u"\N{DEGREE SIGN}C")  # Using UTF8 to get a degree symbol.
humidityMeter2 = meterType2(vector(2.25, -1.25, -0.1), color.blue, 0, 100, "DHT22 Hum", "%")

# Now lets stamp my logo and name on the meter display... and "EasiFace" is my logo - you need your own!
myLogoL1 = "EasiFace"
for letterCounter, theta in zip(range(len(myLogoL1)), np.linspace(5 * np.pi / 8, 3 * np.pi / 8, len(myLogoL1))):
    logo1Letter = myLogoL1[letterCounter]
    logo1Character = text(text = logo1Letter, color = color.green, opacity = 1, align = "center", height = 0.2, pos = vector(2.1 * np.cos(theta), 2.1 * np.sin(theta) - 3, -0.035), axis = vector(1, 0, 0))
    logo1Character.rotate(angle = theta - np.pi / 2, axis = vector(0, 0, 1))
myLogoL2 = "MeterPanel" # Warning - I found that when this text had a space in it, it broke vPython.
for letterCounter, theta in zip(range(len(myLogoL2)), np.linspace(5 * np.pi / 8, 3 * np.pi / 8, len(myLogoL2))):
    logo2Letter = myLogoL2[letterCounter]
    logo2Character = text(text = logo2Letter, color = color.green, opacity = 1, align = "center", height = 0.2, pos = vector(1.9 * np.cos(theta), 1.8 * np.sin(theta) - 3, -0.035), axis = vector(1, 0, 0))
    logo2Character.rotate(angle = theta - np.pi / 2, axis = vector(0, 0, 1))
# Next, lets put a pyramid below the logo, just because we can.
pyramid(pos = vector(0, -2, 0), color = color.green, size = vector(0.5, 0.25, 0.25), axis = vector(0, 1, 0))
# Finally, lets mount it all on a dark gray metal panel and screw that onto the canvas.
box(color = color.gray(0.5), texture = textures.metal, size = vector(7, 4.5, 0.1), pos = vector(0, -0.25, -0.2))
drawScrew(vector(-3.4, 1.9, -0.23))
drawScrew(vector(3.4, 1.9, -0.23))
drawScrew(vector(-3.4, -2.4, -0.23))
drawScrew(vector(3.4, -2.4, -0.23))

# Connect to the Arduino on the correct serial port!
if not pseudoDataMode: # We are not meter testing with pseudo random data.
    serialOK = True
    try:
        # My Arduino happens to connect as serial port 'com3'. Yours may be different!
        arduinoDataStream = serial.Serial('com3', 115200)
        # Give the serial port time to connect.
        time.sleep(1)
    except serial.SerialException as err:
        serialOK = False
        # Put an error message on top of the meter.
        serialErrorVisible = 0
        serialError = text(text = "-Serial Error-", color = color.red, opacity = serialErrorVisible, align = "center", height = 0.5, pos = vector(0, -0.25, 0.25), axis = vector(1, 0, 0))
        print("Serial Error: %s." % (str(err)[0].upper() + str(err)[1:])) # A cosmetic fix to uppercase the first letter of err.

# Initialise the sensor reading variables.
pot1Value = "-1" # Invalid.
tDHT11 = hDHT11 = tDHT22 = hDHT22 = "nan" # Invalid.

# An infinite loop...
while True:
    # Set the vPython refresh rate.
    rate(vPythonRefreshRate)
    if not pseudoDataMode: # We are not meter testing with pseudo random data.
        if serialOK:
            # Wait until data has been received from the Arduino.
            while arduinoDataStream.in_waiting == 0:
                rate(vPythonRefreshRate)
            # Read the CSV data from the Arduino.
            arduinoDataPacket = arduinoDataStream.readline()
            # Convert the CSV data from a byte stream to a CSV string.
            arduinoDataPacket = str(arduinoDataPacket, 'utf-8')
            # Strip the CRLF from the end of the CSV string.
            arduinoDataPacket = arduinoDataPacket.strip('\r\n')
            # Convert the CSV string into separate variables.
            (pot1Value, tDHT11, hDHT11, tDHT22, hDHT22) = arduinoDataPacket.split(",")
            # Check the returned data and convert the variables to numbers.
            # NaN is a valid float number value and means "not a number", i.e. the Arduino has no valid data for this measurement.
            if pot1Value != "-1":
                pot1Value = int(pot1Value)
            if tDHT11 != "nan":
                tDHT11   = float(tDHT11)
            if hDHT11 != "nan":
                hDHT11   = float(hDHT11)
            if tDHT22 != "nan":
                tDHT22   = float(tDHT22)
            if hDHT22 != "nan":
                hDHT22   = float(hDHT22)
        else:
            # Flash the serial error message on top of the meter.
            serialErrorVisible = (serialErrorVisible + 1) % 2 # Using modulo 2 maths to toggle the variable between 0 and 1.
            serialError.opacity = serialErrorVisible
            # Wait for a bit...
            time.sleep(0.5)
    else: # Get some pseudo random data to test the meters.
        (pot1Value, tDHT11, hDHT11, tDHT22, hDHT22) = pseudoData()

    # Update the meters with the latest measurements.
    if pot1Value != "-1":
        pot1Voltage = round(5 * pot1Value / 1024, 2) # Calculate the voltage represented by this sensor value.
    else:
        pot1Voltage = "nan"
    voltageMeter1.update(pot1Voltage, pot1Value) # Send this meter the calculated float voltage and the raw integer value.
    # Update these meters less frequently if we are using pseudo random data.
    pseudoDataCounter = (pseudoDataCounter + 1) % 10
    if not pseudoDataMode or pseudoDataCounter == 0:
        thermoMeter1.update(tDHT11)
        humidityMeter1.update(hDHT11)
        thermoMeter2.update(tDHT22)
        humidityMeter2.update(hDHT22)

# EOF
