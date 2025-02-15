
import os
import logging
import sys
from traceback import format_exception
import argparse
import datetime
import time





import core





def definePathDict(programName, customOutputFolderName, commonfunctionsPath, parameterProfile=None):
    try:
        pathDict
    except NameError:
        pathDict = {}

    
    
    pathDict['Output_Folder_Root'] = core.getParameter('AA_OUTPUT_FOLDER_ROOT', parameterProfile=parameterProfile)
    if not pathDict['Output_Folder_Root']:
        print("Variable AA_OUTPUT_FOLDER_ROOT is not defined as an environment variable.")
        sys.exit(1)


    core.createFolderIfNotExisting(pathDict['Output_Folder_Root'])   

    pathDict['Output_Folder_Middle_Path'] = os.path.join(pathDict['Output_Folder_Root'], programName)
    
    core.createFolderIfNotExisting(pathDict['Output_Folder_Middle_Path'])  

    pathDict['Output_Folder_Name'] = False
    


    if (programName in ['program_scheduling', 'health_check']) and (os.name == 'posix'):
        pathDict['Output_Folder_Name'] = datetime.datetime.now().strftime('%d-%b-%Y_%H-%M')
    
    
    if not pathDict['Output_Folder_Name']:
        if (customOutputFolderName != None):
            pathDict['Output_Folder_Name'] = customOutputFolderName    
    
    

    if not pathDict['Output_Folder_Name']:
        if os.name in ['nt', 'posix']:
            yamlFile = core.getValueFromEnvironmentVariable('AA_PROGRAM_PARAMETERS_FULL')
            if yamlFile:
                if os.path.exists(yamlFile):
                    fullParametersDict = readYamlToDictionary(yamlFile)
                    outputFolderDefDict = fullParametersDict['OUTPUT_FOLDER_DEFINITIONS']
                    if programName in outputFolderDefDict.keys():
                        pathDict['Output_Folder_Name'] = outputFolderDefDict[programName]            


    if not pathDict['Output_Folder_Name']:
        pathDict['Output_Folder_Name'] = core.getValueFromEnvironmentVariable('AA_OUTPUT_FOLDER_NAME')
        

    if not pathDict['Output_Folder_Name']:
        if os.name in ['nt', 'posix']:
            value = input('Enter Output Folder Name: ')
            os.environ['AA_OUTPUT_FOLDER_NAME'] = value
            pathDict['Output_Folder_Name'] = value
        else:
            print("Environment variable AA_OUTPUT_FOLDER_NAME is not defined.")
            sys.exit(1)

    pathDict['Output_Folder'] = os.path.join(pathDict['Output_Folder_Middle_Path'], pathDict['Output_Folder_Name'])
    
    core.createFolderIfNotExisting(pathDict['Output_Folder'])  

    pathDict['Git_Repository_Path'] = core.getParameter('AA_GIT_REPOSITORY_PATH', parameterProfile=parameterProfile)
    if not pathDict['Git_Repository_Path']:
        print("Variable AA_GIT_REPOSITORY_PATH is not defined in as an environment variable.")
        sys.exit(1)


    pathDict['Common_Folder'] = commonfunctionsPath

    pathDict['Program_Folder'] = os.path.join(pathDict['Git_Repository_Path'], 'folders', programName)

    pathDict["Log_Folder"] = os.path.join(pathDict['Output_Folder'], 'log')
    core.createFolderIfNotExisting(pathDict['Log_Folder'])  

    pathDict["Data_Folder"] = os.path.join(pathDict['Output_Folder'], 'data')
    core.createFolderIfNotExisting(pathDict['Data_Folder'])

    pathDict["Input_Folder"] = os.path.join(pathDict['Output_Folder_Middle_Path'], 'input')
    core.createFolderIfNotExisting(pathDict['Input_Folder'])

    return pathDict






def defineBasicPathDict(commonfunctionsPath):
    try:
        pathDict
    except NameError:
        pathDict = {}    

    pathDict['Git_Repository_Path'] = core.getValueFromEnvironmentVariable('AA_GIT_REPOSITORY_PATH')
    if not pathDict['Git_Repository_Path']:
        print("Environment variable AA_GIT_REPOSITORY_PATH is not defined.")
        sys.exit(1)


    pathDict['Common_Folder'] = commonfunctionsPath
    
    return pathDict





def getTempDir(folderName):
    if os.name == 'nt':
        repoDir = rf"C:\temp\{folderName}"
    else:
        repoDir = rf"/tmp/{folderName}"
    
    return repoDir



def initiateLogger(logfilename=None, pathDict=None, consoleLogLevel=logging.DEBUG, timeInUTC=False):
    # Logging settings
    logToFile = False
    
    if pathDict != None:
        if 'Log_Folder' in pathDict.keys():
            logToFile = True
        
    if logToFile:
        logfilefullpath = os.path.join(pathDict['Log_Folder'], logfilename)

    rootlogger = logging.getLogger()
    rootlogger.setLevel(logging.DEBUG)


    # Create a file handler
    if logToFile:
        handler = logging.FileHandler(logfilefullpath, encoding='utf8')
        handler.setLevel(logging.DEBUG)


    # Create a console handler
    console = logging.StreamHandler()
    console.setLevel(consoleLogLevel)


    # Create a logging format
    if not timeInUTC:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %I:%M:%S %p')
    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %I:%M:%S %p UTC')
        formatter.converter = time.gmtime
    console.setFormatter(formatter)
    if logToFile:
        handler.setFormatter(formatter)


    # Add the handlers to the rootlogger
    if not len(rootlogger.handlers):
        rootlogger.addHandler(console)
        if logToFile:
            rootlogger.addHandler(handler) 
        
    
    def my_handler(type_, value, tb):
        exceptionDetails = format_exception(type_, value, tb)
        for i in range(0, len(exceptionDetails)):
            if i == 0:
                rootlogger.exception(f"Uncaught exception: {exceptionDetails[i]}")
            else:
                rootlogger.exception(f"{exceptionDetails[i]}")

    # Install exception handler
    sys.excepthook = my_handler
    
    
    if pathDict != None:
        if 'Output_Folder_Name' in pathDict.keys():
            rootlogger.info(f"Output_Folder_Name: '{pathDict['Output_Folder_Name']}'")
        if 'Output_Folder' in pathDict.keys():
            rootlogger.info(f"Output_Folder: '{pathDict['Output_Folder']}'")

    if logToFile:
        rootlogger.info(f"Created log file at: {logfilefullpath}")





def setLoggerLevel(loggerNameList, loggingLevel):
    for loggerName in loggerNameList:
        logging.getLogger(loggerName).setLevel(loggingLevel)


#%%
        
def adjustLogLevel(loggerName, logLevel):
    
    suppressLogsList = [loggerName]
    
    
    levelDict = {
            'INFO' : logging.INFO,
            'WARNING' : logging.WARNING,
            'DEBUG' : logging.DEBUG,
            'ERROR' : logging.ERROR,
            'CRITICAL' : logging.CRITICAL,
        }
    
    loggingLevel = levelDict[logLevel]

    setLoggerLevel(loggerNameList=suppressLogsList, loggingLevel=loggingLevel)    
    

#%%

class SuppressLogs:
    def __init__(self, loggerNameList, logLevel):
        self.loggerNameList = loggerNameList
        self.logLevel = logLevel
        self.logLevelDict = {}
        self.set()
    def set(self):
        for loggerName in self.loggerNameList:
            logger = logging.getLogger(loggerName)
            self.logLevelDict['loggerName'] = logger.level
            adjustLogLevel(loggerName=loggerName, logLevel=self.logLevel)
    def release(self):
        for loggerName in self.loggerNameList:
            logger = logging.getLogger(loggerName)
            setLoggerLevel(loggerNameList=[loggerName], loggingLevel=self.logLevelDict['loggerName'])  
     



adjustAsyncioLogLevel = SuppressLogs(loggerNameList=['asyncio'], logLevel='INFO')




def logCommandLineArguments(locallogger):
    argumentLine = " ".join(sys.argv)
    locallogger.info(f"Command Line Invokation: python {argumentLine}")
    



