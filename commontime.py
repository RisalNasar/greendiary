

import os, sys, datetime




class TimeIntervalGenerator:
    def __init__(self, startTime, timeIntervalExtraDelta, timeInterval,  endTime):
        self.startTime = startTime
        self.endTime = endTime
        self.timeInterval = timeInterval
        self.timeIntervalExtraDelta = timeIntervalExtraDelta
        self.iterationStartTime = startTime
        self.iterationEndTime = startTime + self.timeInterval
        self.iterationCount = 1
        self.finishedIteration = False
    def nextIteration(self, outputStringformat):
        # stringformat="%Y-%m-%dT%H:%M:%S%z"
        outputDictionary = {
            "Iteration_Count" : 0,
            "Iteration_Start_Time" : "",
            "Iteration_End_Time" : "",
        }
        if not self.finishedIteration:
            if self.iterationStartTime <= self.endTime:
                if self.iterationEndTime < self.endTime:
                    outputDictionary['Iteration_Count'] = self.iterationCount
                    outputDictionary['Iteration_Start_Time'] = datetime.datetime.strftime(self.iterationStartTime, outputStringformat)
                    outputDictionary['Iteration_End_Time'] = datetime.datetime.strftime(self.iterationEndTime, outputStringformat)
                    # Next interation exists.  Prepare for next iteration.
                    self.iterationCount = self.iterationCount + 1
                    self.iterationStartTime = self.iterationStartTime + self.timeInterval + self.timeIntervalExtraDelta
                    self.iterationEndTime = self.iterationStartTime + self.timeInterval
                else:
                    # Last iteration reached.
                    self.iterationEndTime = self.endTime
                    outputDictionary['Iteration_Count'] = self.iterationCount
                    outputDictionary['Iteration_Start_Time'] = datetime.datetime.strftime(self.iterationStartTime, outputStringformat)
                    outputDictionary['Iteration_End_Time'] = datetime.datetime.strftime(self.iterationEndTime, outputStringformat)
                    self.finishedIteration = True
            else:
                # Invalid interval
                self.finishedIteration = True
                outputDictionary = False
        else:
            outputDictionary = False
        return outputDictionary






def getDateTimeFromString(stringValue, dateTimeStringFormat="%Y-%m-%dT%H:%M:%S.%f%z", output='datetime'):
    if type(stringValue) != str:
        return stringValue
    else:
        stringValue = stringValue.strip()
        if stringValue == "":
            return stringValue
        dateTimeValue = datetime.datetime.strptime(stringValue, dateTimeStringFormat)
        if output == 'datetime':
            return dateTimeValue
        elif output == 'date':
            return dateTimeValue.date()
        














