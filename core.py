

import os
import sys
import logging
import yaml
import time
import datetime 
import requests
from importlib import reload




def checkIfInIPython():
    try:
        get_ipython().config 
        in_ipython = True
    except NameError:
        in_ipython = False
    return in_ipython




def getValueFromEnvironmentVariable(name):
    locallogger = logging.getLogger(f'{__name__}.getValueFromEnvironmentVariable')
    
    try:
        name = str(name)
        value = os.environ[name]
        #locallogger.debug(f"Attempted Retrieval from Environment Variable: '{name}'")
    except KeyError:
        #locallogger.info(f"{name} is not defined as an environment variable.")
        #sys.exit(1)
        return False
    return value




def getParameter(parameterName, parameterProfile=None):
    
    if parameterProfile != None:
        
        if getValueFromEnvironmentVariable('AA_PROGRAM_PARAMETERS_FULL') != False:
            # Parameters to be read from Config file
            paraDictFull = getParametersDict('AA_PROGRAM_PARAMETERS_FULL')
            
            if parameterProfile in paraDictFull.keys():
                paraDict = paraDictFull[parameterProfile]
            
                if parameterName in paraDict.keys():
                    
                    if getValueFromEnvironmentVariable('COMMON_MODE') != 'Production':
                        if parameterName in ['ANALYTICS_CODE_MODE', 'AA_OUTPUT_FOLDER_ROOT']:
                            if paraDict[parameterName] in ['Production', r'P:\results']:
                                seekManualAcknowledgement()
                    
                    return paraDict[parameterName]
    
    # if getValueFromEnvironmentVariable('PARAMETERS_OVERRIDE') != False:
    #     # Parameters to be overridden
    #     paraDict = getParametersDict('PARAMETERS_OVERRIDE')
    yamlFile = getValueFromEnvironmentVariable('AA_PROGRAM_PARAMETERS_FULL')
    if yamlFile:
        if os.path.exists(yamlFile):
            fullParametersDict = readYamlToDictionary(yamlFile)
            paraDict = fullParametersDict['PARAMETERS_OVERRIDE']
            if parameterName in paraDict.keys():
                
                if parameterName in ['ANALYTICS_CODE_MODE', 'AA_OUTPUT_FOLDER_ROOT']:
                    if paraDict[parameterName] in ['Production', r'P:\results']:
                        seekManualAcknowledgement()
                
                return paraDict[parameterName]
    return getValueFromEnvironmentVariable(parameterName)
        




def createFolderIfNotExisting(folderPath):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath) 



def getParametersDict(parameterFileKey):
    locallogger = logging.getLogger(f"{__name__}.getParametersDict")
    yamlFile = getParameter(parameterFileKey)
    if not yamlFile:
        locallogger.error(f"Environment variable {parameterFileKey} is not defined!")
        sys.exit(1)
    else:
        if not os.path.exists(yamlFile):
            locallogger.error(f"Parameter file does not exist at location: '{yamlFile}'")
            sys.exit(1)
        else:
            parametersDict = readYamlToDictionary(yamlFile)
            return parametersDict
    





def readYamlToDictionary(yamlFile):
    
    with open(yamlFile, 'r') as stream:
        try:
            dictContent = yaml.safe_load(stream)
            #print(yamlConfig)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
    return dictContent





# ---------------------------------------------------------------------------------------------------------------- 
#%%


def getResponseFromURL(url, method, headers=None, auth=None,  proxies=None, data=None, json=None, files=None, params=None, cookies=None, verify=False, timeout=120, session=None, loggingPrefix=None, responseEncoding=None, maxRetry=3, sleepCodeList=None, sleepSeconds=3, returnJson=False, trustEnvironment=False):
    locallogger = getLocalLogger(localloggername='getResponseFromURL', rootFileName=__name__, loggingPrefix=loggingPrefix)

    response = None
    responsecode = None    
    jresponse = None

    issueInResponse = 0

    if trustEnvironment == False:
        if session == None:
            session = requests.Session()
        session.trust_env = False

    ######### TESTING #################
    # return None
    ###################################
        
    while True:
        try:
            locallogger.info(f"Reaching out to url: {url}")
            if method == 'GET':
                if session == None:
                    response = requests.get(url, headers=headers, params=params, cookies=cookies, auth=auth, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.get(url, headers=headers, params=params, cookies=cookies, auth=auth, proxies=proxies, verify=verify, timeout=timeout)
            elif method == 'POST':
                if session == None:
                    response = requests.post(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, files=files, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.post(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, files=files, proxies=proxies, verify=verify, timeout=timeout)
            elif method == 'PUT':
                if session == None:
                    response = requests.put(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.put(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
            elif method == 'DELETE':
                if session == None:
                    response = requests.delete(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.delete(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
            else:
                locallogger.error(f"Method provided: {method} is not GET, POST, PUT or DELETE.")
                sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            locallogger.exception(f'Exception happened.')
            issueInResponse = issueInResponse + 1
            locallogger.warning(f"issueInResponse incremenented to: {issueInResponse}.")
            if 'ConnectionResetError' in str(e):
                locallogger.warning(f"Connection Reset Happened.  Sleeping for {sleepSeconds} seconds")
                time.sleep(sleepSeconds)                
        if response != None:
            responsecode = response.status_code
            locallogger.info(f'Received response code: {responsecode}')
            if responsecode in [200, 201]:
                retry = False
                if responseEncoding != None:
                    response.encoding = responseEncoding
                    
                    # If response.encoding is not specifically set, sometimes, chardet will take a looong time to detect the encoding.
                    # https://github.com/psf/requests/issues/2359
                
                
                if returnJson == True:
                    
                    try:
                        #jsonString = response.text
                        jresponse = response.json()
                        #jresponse = json.loads(jsonString, strict=False)
                    except Exception:
                        locallogger.exception(f"Could not decode into JSON!")
                        retry = True
                    
                    if retry == False:
                        return response, jresponse
                
                if retry == False:
                    return response

            # Manage any cookies returned
            try:
                cookieDict = {}
                cookieDict = response.cookies.get_dict()
                if cookieDict != {}:
                    cookies = cookieDict
                    if maxRetry <= 1:
                        locallogger.info(f"Cookies were returned.  maxRetry set to 2, and trying again...")
            except Exception:
                pass
            
            
            if responsecode == 429: # Rate limiting
                locallogger.warning(f"Rate-Limiting encountered.  Sleeping for {sleepSeconds} seconds")
                time.sleep(sleepSeconds)
            elif responsecode == 404:
                locallogger.warning(f"responsecode: {responsecode}; responsetext: {response.text}")
                return response
            else:
                locallogger.warning(f"responsecode: {responsecode}; responsetext: {response.text}")
            
            if sleepCodeList != None and sleepSeconds != None:
                if responsecode in sleepCodeList:
                    
                    sleepSeconds = int(sleepSeconds)
                    
                    locallogger.warning(f"Sleep code encountered.  Sleeping for {sleepSeconds} seconds")
                    time.sleep(sleepSeconds)
                    
                    #sleepSeconds = sleepSeconds * sleepMultiplier
                
            issueInResponse = issueInResponse + 1
            locallogger.warning(f"issueInResponse incremenented to: {issueInResponse}.")
        if issueInResponse >= maxRetry:
            locallogger.warning(f"Skipping URL '{url}' due to non-receipt of required data.")
            break
    if returnJson == True:
        return response, jresponse
    return response

#%%

def getResponseFromURLWithDataPullStatus(url, method, headers=None, auth=None,  proxies=None, data=None, json=None, params=None, cookies=None, verify=False, timeout=120, session=None, loggingPrefix=None, responseEncoding=None, maxRetry=3, sleepCodeList=None, sleepSeconds=300, returnJson=False):
    if loggingPrefix == None:
        locallogger = logging.getLogger(f'{__name__}.getResponseFromURL')
    else:
        locallogger = logging.getLogger(f'{loggingPrefix}.{__name__}.getResponseFromURL')
    #   

    response = None
    responsecode = None    
    dataPullStatus = 'Failed'
    jresponse = None

    issueInResponse = 0
        
    while True:
        try:
            locallogger.info(f"Reaching out to url: {url}")
            if method == 'GET':
                if session == None:
                    response = requests.get(url, headers=headers, params=params, cookies=cookies, auth=auth, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.get(url, headers=headers, params=params, cookies=cookies, auth=auth, proxies=proxies, verify=verify, timeout=timeout)
            elif method == 'POST':
                if session == None:
                    response = requests.post(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.post(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
            elif method == 'PUT':
                if session == None:
                    response = requests.put(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.put(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
            elif method == 'DELETE':
                if session == None:
                    response = requests.delete(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
                else:
                    response = session.delete(url, headers=headers, params=params, cookies=cookies, data=data, auth=auth, json=json, proxies=proxies, verify=verify, timeout=timeout)
            else:
                locallogger.error(f"Method provided: {method} is not GET, POST, PUT or DELETE.")
                sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            locallogger.exception(f'Exception happened.')
            issueInResponse = issueInResponse + 1
            locallogger.warning(f"issueInResponse incremenented to: {issueInResponse}.")
            if 'ConnectionResetError' in str(e):
                locallogger.warning(f"Connection Reset Happened.  Sleeping for {sleepSeconds} seconds")
                time.sleep(sleepSeconds)                
        if response != None:
            responsecode = response.status_code
            locallogger.info(f'Received response code: {responsecode}')
            if responsecode in [200, 201]:
                retry = False
                if responseEncoding != None:
                    response.encoding = responseEncoding
                    
                    # If response.encoding is not specifically set, sometimes, chardet will take a looong time to detect the encoding.
                    # https://github.com/psf/requests/issues/2359
                dataPullStatus = 'Successful'
                
                
                if returnJson == True:
                    
                    try:
                        #jsonString = response.text
                        jresponse = response.json()
                        #jresponse = json.loads(jsonString, strict=False)
                    except Exception:
                        locallogger.exception(f"Could not decode into JSON!")
                        retry = True
                    
                    if retry == False:
                        return response, jresponse, dataPullStatus
                
                if retry == False:
                    return response, dataPullStatus

            # Manage any cookies returned
            try:
                cookieDict = {}
                cookieDict = response.cookies.get_dict()
                if cookieDict != {}:
                    cookies = cookieDict
                    if maxRetry <= 1:
                        locallogger.info(f"Cookies were returned.  maxRetry set to 2, and trying again...")
            except Exception:
                pass
            
            locallogger.warning(f"responsecode: {responsecode}; responsetext: {response.text}")
            if responsecode == 429: # Rate limiting
                locallogger.warning(f"Rate-Limiting encountered.  Sleeping for {sleepSeconds} seconds")
                time.sleep(sleepSeconds)
            
            if sleepCodeList != None and sleepSeconds != None:
                if responsecode in sleepCodeList:
                    
                    sleepSeconds = int(sleepSeconds)
                    
                    locallogger.warning(f"Sleep code encountered.  Sleeping for {sleepSeconds} seconds")
                    time.sleep(sleepSeconds)
                    
                    #sleepSeconds = sleepSeconds * sleepMultiplier
                
            issueInResponse = issueInResponse + 1
            locallogger.warning(f"issueInResponse incremenented to: {issueInResponse}.")
        if issueInResponse >= maxRetry:
            locallogger.warning(f"Skipping URL '{url}' due to non-receipt of required data.")
            break
    if returnJson == True:
        return response, jresponse, dataPullStatus
    return response, dataPullStatus






# %% ================================================== Timely Operation =====================================================================================

class TimelyOperation:

    def __init__(self, timeDeltaWindow, operationFunction, state=None):
        self.startTime = datetime.datetime.now()
        self.timeDeltaWindow = timeDeltaWindow
        self.operationFunction = operationFunction
        self.state = state
        if self.state != None:
            self.startTime = self.state.getSet(key="startTime", value=self.startTime, showSaveLog=False)
           

    def operate(self, *args):
        returnObject = None
        nowTime = datetime.datetime.now()
        if nowTime >= (self.startTime + self.timeDeltaWindow):
            returnObject = self.operationFunction(*args)
            self.startTime = nowTime
            if self.state != None:
                self.state.update(key="startTime", value=self.startTime, showSaveLog=False)
        return returnObject



def getLocalLogger(localloggername, rootFileName, loggingPrefix=None):
    if loggingPrefix == None:
        locallogger = logging.getLogger(f'{rootFileName}.{localloggername}')
    else:
        locallogger = logging.getLogger(f'{loggingPrefix}.{localloggername}')
    return locallogger




class RetryOperation:
    def __init__(self, operationName, retryThreshold,  exitProgramIfAllRetriesFailed=True, loggingPrefix=None):
        self.locallogger = getLocalLogger(localloggername='RetryOperation', rootFileName=__name__, loggingPrefix=loggingPrefix)
        self.operationName = operationName
        self.retryThreshold = retryThreshold
        self.numberOfTries = 0
        self.retry = True
        self.exitProgramIfAllRetriesFailed = exitProgramIfAllRetriesFailed
    def attempt(self):
        if self.retry:
            if self.numberOfTries >= self.retryThreshold:
                self.retry = False
                self.locallogger.error(f"Retried operation '{self.operationName}'  {self.numberOfTries} times.  All attempts failed!")
                if self.exitProgramIfAllRetriesFailed:
                    sys.exit(1)
        if self.retry:
            self.numberOfTries = self.numberOfTries + 1
        return self.retry 
    def flagSuccess(self):
        self.retry = False




def timeHumanFormat(timeValueInSeconds):
    timeValueInMinutes = float(timeValueInSeconds) / 60
    if timeValueInMinutes > 60:
        timeInHours = int(timeValueInMinutes/60)
        timeInMinues = (timeValueInMinutes % 60)
        timeInMinues = round(timeInMinues, 2)
        timeString = f"{timeInHours} hours, {timeInMinues} minutes"  
    else:
        timeInMinues = timeValueInMinutes
        timeInMinues = round(timeInMinues, 2)
        timeString = f"{timeInMinues} minutes"
    return timeString  
    



class Timer:
    def __init__(self):
        self.timerStartTime = time.time()
        self.timerStopTime = None
    def restartTimer(self):
        self.__init__()
    def stopTimer(self):
        self.timerStopTime = time.time()
    def getTimerTimeRaw(self):
        if self.timerStopTime == None:
            timerStopTime = time.time()
        else:
            timerStopTime = self.timerStopTime
        processingTimeRaw = (timerStopTime - self.timerStartTime)
        return processingTimeRaw
    def getTimerTime(self):
        if self.timerStopTime == None:
            timerStopTime = time.time()
        else:
            timerStopTime = self.timerStopTime
        processingTimeInSeconds = float(timerStopTime - self.timerStartTime)
        timeString = timeHumanFormat(timeValueInSeconds=processingTimeInSeconds)
        return timeString



def extractStringIntoListofStrings(fullString):
    splitList = fullString.split(',')
    splitListSpaceRemoved = []
    for item in splitList:
        splitListSpaceRemoved.append(item.strip())
    return splitListSpaceRemoved




def waitForKeyPress():
    keyPressed = input('Press any key to continue.  Press q to quit: ') # For debugging
    if keyPressed == 'q':
        sys.exit(0)











class ProgressTracker:
    def __init__(self, totalIterationValue):
        self.currentIteration = 0
        self.exponentialIteration = 1
        self.percentageForReporting = 5
        self.totalIteration = totalIterationValue
        #self.operationStartTime = time.time()
        self.timer = Timer()
    def progressReport(self, logger, alwaysReport=False, numberOfIterationsToTrigger=False):
        trigger = False
        self.currentIteration = self.currentIteration + 1
        if numberOfIterationsToTrigger != False:
            if (self.currentIteration % numberOfIterationsToTrigger == 0):
                trigger = True
        percentage = (float(self.currentIteration)/self.totalIteration)*100
        report = False
        action = False
        if (self.currentIteration >= self.exponentialIteration) and (percentage < 5):
            self.exponentialIteration = self.exponentialIteration * 2
            report = True
        if percentage >= self.percentageForReporting:
            self.percentageForReporting = self.percentageForReporting + 5
            report = True
            action = True
        if report or alwaysReport:
            percentage = round(percentage, 2)
            elapsedTimeRaw = self.timer.getTimerTimeRaw()
            elapsedTimeFormatted = self.timer.getTimerTime()
            dateFormat='%d-%b-%Y %I:%M %p'
            projectedTotalTime = float(elapsedTimeRaw * self.totalIteration) / self.currentIteration
            projectedTimeRemaining = (projectedTotalTime - elapsedTimeRaw)
            projectedTimeRemainingFormatted = timeHumanFormat(timeValueInSeconds=projectedTimeRemaining)
            projectedEndTime = self.timer.timerStartTime + projectedTotalTime
            projectedEndTimeFormatted = time.strftime(dateFormat, time.localtime(projectedEndTime))
            logger.info(f'Progress: {percentage} %, Elapsed Time: {elapsedTimeFormatted}, Projected Time Remaining: {projectedTimeRemainingFormatted}, Projected End Time: {projectedEndTimeFormatted}')
        if action or trigger:
            return True
        return False  



