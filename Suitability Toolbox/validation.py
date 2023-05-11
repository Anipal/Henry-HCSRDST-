import arcpy
import numpy as np
from execution import parseargs

class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        return

    # def isLicensed(self):
    #     # set tool isLicensed.
    # return True

    # def postExecute(self):
    #     # This method takes place after outputs are processed and
    #     # added to the display.
    # return

if __name__ == 'main':
    #Get arguments
    args = parseargs()

    #Ensure weights add up to 1
    weights = args[2]

    #Provide a little bit of leeway
    if abs(1 - np.sum(weights)) > 0.01:
        arcpy.AddError("Weights must add up to 1: {} != 1".format(np.sum(weights)))