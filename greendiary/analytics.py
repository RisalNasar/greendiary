


import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
import datetime
import pickle
import shutil
import glob
import math
from importlib import reload
import json


from . import commonmath
from . import core



# Read data in CSV to dataframe
def readCSV(folderPath=None, fileName=None, filePath=None):
    locallogger = logging.getLogger(f"{__name__}.readCSV")
    
    if filePath == None:
        if (folderPath != None) and (fileName != None):
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileName are None.")
            sys.exit(1)    
    filePathObject = Path(filePath)
    if not filePathObject.is_file():
        locallogger.error(f"File does not exist: {filePath}")
        sys.exit(1)
    locallogger.info(f"Reading excel file at: '{filePath}'")
    do_df = pd.read_csv(filePath, parse_dates=False)
    do_df = replaceNullValuesInDataframe(df=do_df)
    return do_df




def replaceNullValuesInDataframe(df, excludedColumnsList=None):
    locallogger = logging.getLogger(f"{__name__}.replaceNullValuesInDataframe")
    if excludedColumnsList != None:
        includedColumnsList = columnListExceptCertainOnes(df, exceptList=excludedColumnsList)
    else:
        includedColumnsList = list(df.columns)
        excludedColumnsList = []
    nullExists = False
    for column in includedColumnsList:  
        if df[column].isnull().values.any():
            # locallogger.warning(f"Column: '{column}' has null values.")
            nullExists = True
    if nullExists:
        df[includedColumnsList] = df[includedColumnsList].replace(np.nan, '', regex=True)
        locallogger.info(f"Relaced null values in the dataframe with empty string.")
    else:
        locallogger.info(f"No null values found.")
    return df






def readExcel(folderPath=None, fileNamePrefix=None, filePath=None, sheetName='data', password=None, literalEvalColumnList=None, dtype=None):
    locallogger = logging.getLogger(f"{__name__}.readExcel")
    
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.xlsx'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)    
    
    if password != None:
        intermediateFilePath = decryptExcel(password=password, filePath=filePath)
        filePathObject = intermediateFilePath
    else:
        filePathObject = Path(filePath)
    if not filePathObject.is_file():
        locallogger.error(f"File does not exist: {filePath}")
        sys.exit(1)
    locallogger.info(f"Reading excel file at: '{filePath}'")
    df = pd.read_excel(filePathObject, sheet_name=sheetName, parse_dates=False, dtype=dtype)
    df = df.replace(np.nan, '', regex=True)
    if password != None:
        time.sleep(100)
        intermediateFilePath.unlink()
    
    if literalEvalColumnList != None:
        for column in literalEvalColumnList:
            df[column] = df[column].apply(lambda x: literal_eval(x))
    
    return df




def encryptExcel(password, folderPath=None, fileNamePrefix=None, filePath=None):
    locallogger = logging.getLogger(f"{__name__}.encryptExcel")

    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.xlsx'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)
    excelFilePath = Path(filePath)
    vbsScript = \
    f"""' Save with password required upon opening

    Set excel_object = CreateObject("Excel.Application")
    Set workbook = excel_object.Workbooks.Open("{excelFilePath}")

    excel_object.DisplayAlerts = False
    excel_object.Visible = False

    workbook.SaveAs "{excelFilePath}", , "{password}"

    excel_object.Application.Quit
    """

    # write vbs script
    vbsScriptPath = excelFilePath.parent.joinpath("set_pw.vbs")
    with open(vbsScriptPath, "w") as file:
        file.write(vbsScript)

    #execute vbs script
    if os.name == 'posix':
        subprocess.call(['wine', 'cscript.exe', str(vbsScriptPath)])
    else:
        subprocess.call(['cscript.exe', str(vbsScriptPath)])

    # remove vbs script file
    vbsScriptPath.unlink()






def decryptExcel(password, folderPath=None, fileNamePrefix=None, filePath=None):
    locallogger = logging.getLogger(f"{__name__}.decryptExcel")

    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.xlsx'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)
    excelFilePath = Path(filePath)
    randomFileName = commonmath.getRandomAlphaNumericString(15)
    tempFilePath = excelFilePath.parent.joinpath(f"{randomFileName}.xlsx")
    
    vbsScript = \
    f"""' Open password protected file

    Set excel_object = CreateObject("Excel.Application")
    Set workbook = excel_object.Workbooks.Open("{excelFilePath}", , , , "{password}")

    excel_object.DisplayAlerts = False
    excel_object.Visible = False

    workbook.SaveAs "{tempFilePath}", , ""

    excel_object.Application.Quit
    """

    # write vbs script
    vbsScriptPath = excelFilePath.parent.joinpath("read_pw_excel.vbs")
    with open(vbsScriptPath, "w") as file:
        file.write(vbsScript)

    #execute vbs script
    if os.name == 'posix':
        subprocess.call(['wine', 'cscript.exe', str(vbsScriptPath)])
    else:
        subprocess.call(['cscript.exe', str(vbsScriptPath)])

    # remove vbs script file
    vbsScriptPath.unlink()
    
    return tempFilePath







def writeExcelOneFile(dfList, sheetNameList=None, folderPath=None, fileNamePrefix=None, filePath=None,  writeIndex=False, password=None, customSettingsDict=None):
    locallogger = logging.getLogger(f"{__name__}.writeExcelOneFile")
    
    if sheetNameList == None:
        sheetNameList = ['data']
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.xlsx'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)
    #locallogger.debug(f"Starting to write excel file: {filePath}")
    #writer = pd.ExcelWriter(filePath, date_format='dd-mmm-yyyy', datetime_format='dd-mmm-yyyy hh:mm:ss')
    writer = pd.ExcelWriter(filePath, date_format='dd-mmm-yyyy', datetime_format='dd-mmm-yyyy hh:mm:ss', engine='xlsxwriter')
    #writer = pd.ExcelWriter(filePath, date_format=None, datetime_format=None, engine='xlsxwriter')
    # Don't convert url-like strings to urls.
    writer.book.strings_to_urls = False
    for i in range(0, len(dfList)):
        dfList[i].to_excel(writer,sheetNameList[i], index=writeIndex, index_label='Index')
    now = datetime.datetime.now()
    timestamp = {'Time Stamp' : now}
    timestampS = pd.Series(timestamp)
    timestampS.to_frame(name='Time Stamp').to_excel(writer, 'Timestamp', index=False)
    #workbook = writer.book
    for sheetName in sheetNameList:
        worksheet = writer.sheets[sheetName]
        worksheet.set_zoom(85)
        worksheet.set_column('A:EZ', 50)
        worksheet.autofilter('A1:EZ1')
        worksheet.freeze_panes(1, 0)
    
    if customSettingsDict != None:
        sheetListToBeCustomed = list(customSettingsDict.keys())
        for sheetName in sheetListToBeCustomed:
            settingsDict = customSettingsDict[sheetName]
            worksheet = writer.sheets[sheetName]
            if 'columnWidthRange' in settingsDict.keys():
                columnWidthRange = settingsDict['columnWidthRange']
                columnWidthValue = settingsDict['columnWidthValue']
                worksheet.set_column(columnWidthRange, columnWidthValue)
            
            if 'freezePaneRows' in settingsDict.keys():
                freezePaneRows = settingsDict['freezePaneRows']
                freezePaneColumns = settingsDict['freezePaneColumns']
                worksheet.freeze_panes(freezePaneRows, freezePaneColumns)            
        
        
    worksheet = writer.sheets['Timestamp']
    worksheet.set_zoom(85)
    worksheet.set_column('A:A', 25)
    writer.close()
    if password != None:
        # Encrypt file
        encryptExcel(password=password, filePath=filePath)
    locallogger.info(f"Excel '{filePath}' written.")




def writeExcel(dfList, sheetNameList='default_list', folderPath=None, fileNamePrefix=None, filePath=None,  writeIndex=False, chunkLimit=None, password=None, includeTodayDate=False, customSettingsDict=None):
    locallogger = logging.getLogger(f"{__name__}.writeExcel")
    
    if sheetNameList == 'default_list':
        sheetNameList = ['data']
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.xlsx'
            if includeTodayDate:
                fileName = f'{fileNamePrefix}_{today_date}.xlsx'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)
    #writer = pd.ExcelWriter(fileName, date_format='dd-mmm-yyyy', datetime_format='dd-mmm-yyyy hh:mm:ss')
    #---------------- Check if df needs to be split ------------------
    df = dfList[0]
    size = df.size
    maxElementLimit = (2000 * 1000)
    if size <= maxElementLimit:
        writeExcelOneFile(dfList, filePath=filePath, sheetNameList=sheetNameList, writeIndex=writeIndex, password=password, customSettingsDict=customSettingsDict)
    else:
        numberOfChunks = math.ceil(float(size)/maxElementLimit)
        locallogger.debug(f"Number of Chunks: {numberOfChunks}, for file with tentative filePath: {filePath}")
        dfsubList = np.array_split(df, numberOfChunks)
        filePathBeforeExt, ext = os.path.splitext(filePath) 
        for i in range(0, len(dfsubList)):
            runningNumber = i + 1
            filePath = f"{filePathBeforeExt}_{runningNumber}_of_{numberOfChunks}.xlsx"
            dfList2 = dfList.copy()
            dfList2[0] = dfsubList[i]
            writeExcelOneFile(dfList2, filePath=filePath, sheetNameList=sheetNameList, writeIndex=writeIndex, password=password, customSettingsDict=customSettingsDict)
            if chunkLimit:
                if runningNumber == chunkLimit:
                    locallogger.info(f"Chunk Limit of {chunkLimit} reached.  Skipping other chunks.")
                    break



def writePickleAndExcel(df, folderPath, fileNamePrefix, includeTodayDateInExcel=False):
    writePickle(df=df, folderPath=folderPath,  fileNamePrefix=fileNamePrefix)
    writeExcel(dfList=[df], folderPath=folderPath, fileNamePrefix=fileNamePrefix, includeTodayDate=includeTodayDateInExcel)










# Write data in dataframe to CSV
# def writeCSV(fileName, do_df):
# 	do_df.to_csv(fileName, sep=',', na_rep='', index=False, encoding='utf-8')



# Write data in dataframe to cSV
def writeCSV(do_df, folderPath=None, fileNamePrefix=None, filePath=None):
    locallogger = logging.getLogger(f"{__name__}.writeCSV")
    
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.csv'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)    
    locallogger.info(f"Writing CSV file to: '{filePath}'")
    do_df.to_csv(filePath, sep=',', na_rep='', index=False, encoding='utf-8')











def writePickle(df, folderPath=None, fileNamePrefix=None, filePath=None, loggingPrefix=None, logLevel=None):
    if loggingPrefix == None:
        locallogger = logging.getLogger(f'{__name__}.writePickle')
    else:
        locallogger = logging.getLogger(f'{loggingPrefix}.{__name__}.writePickle')
        
        
    if logLevel != None:
        adjustLogLevel(loggerName=locallogger.name, logLevel=logLevel)
        
        
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.pickle'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)            
    df.to_pickle(filePath)
    locallogger.info(f"Dataframe written to pickle file : {filePath}")





def writeObjectToPickle(objectValue, folderPath=None, fileNamePrefix=None, filePath=None, logInfoMessage=True):
    locallogger = logging.getLogger(f"{__name__}.writeObjectToPickle")
    
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.pickle'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)            
    with open(filePath, 'wb') as handle:
        pickle.dump(objectValue, handle, protocol=pickle.HIGHEST_PROTOCOL)
    if logInfoMessage:
        locallogger.info(f"Object written to pickle file : {filePath}")    






def readPickle(folderPath=None, fileNamePrefix=None, filePath=None):
    locallogger = logging.getLogger(f"{__name__}.readPickle")
    
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.pickle'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)
    filePathObject = Path(filePath)
    if not filePathObject.is_file():
        locallogger.error(f"File does not exist: {filePath}")
        sys.exit(1)
    locallogger.info(f"Reading pickle file: {filePath}")
    df = pd.read_pickle(filePath)
    return df







def readPickleToObject(folderPath=None, fileNamePrefix=None, filePath=None, showLog=True):
    locallogger = logging.getLogger(f"{__name__}.readPickleToObject")
    
    if filePath == None:
        if (folderPath != None) and (fileNamePrefix != None):
            fileName = f'{fileNamePrefix}.pickle'
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileNamePrefix are None.")
            sys.exit(1)
    filePathObject = Path(filePath)
    if not filePathObject.is_file():
        locallogger.error(f"File does not exist: {filePath}")
        sys.exit(1)
    with open(filePath, 'rb') as handle:
        objectValue = pickle.load(handle)
    if showLog:
        locallogger.info(f"Reading pickle file: {filePath}")
    return objectValue



def readFile(folderPath=None, fileName=None, filePath=None, mode='r', encoding='utf-8', loggingPrefix=None, logLevel=None):
    if loggingPrefix == None:
        locallogger = logging.getLogger(f'{__name__}.readFile')
    else:
        locallogger = logging.getLogger(f'{loggingPrefix}.{__name__}.readFile')
        
        
    if logLevel != None:
        adjustLogLevel(loggerName=locallogger.name, logLevel=logLevel)
    
    if filePath == None:
        if (folderPath != None) and (fileName != None):
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileName are None.")
            sys.exit(1)
    filePathObject = Path(filePath)
    if not filePathObject.is_file():
        locallogger.error(f"File does not exist: {filePath}")
        sys.exit(1)
    try:
        if mode in ['r', 'w', 'r+', 'w+', 'rw']:
            with open(filePath, mode, encoding=encoding) as file:
                content = file.read()
        elif mode in ['rb', 'wb', 'rwb']:
            with open(filePath, mode) as file:
                content = file.read()
    except FileNotFoundError:
        locallogger.error(f"{filePath} not found.")
        sys.exit(1)
    locallogger.info(f"Read file at filePath {filePath}")
    return content


def readXML(folderPath=None, fileName=None, filePath=None, mode='r', encoding='utf-8', loggingPrefix=None):
   
    contentString = readFile(folderPath=folderPath, fileName=fileName, filePath=filePath, mode=mode, encoding=encoding, loggingPrefix=loggingPrefix)
    
    root = ET.fromstring(contentString)
    
    return root




def writeJSONFile(fileName, jresponse, folderPath, loggingPrefix):
    locallogger = core.getLocalLogger(localloggername='writeJSONFile', rootFileName=__name__, loggingPrefix=loggingPrefix)
    
    
    jsonPretty = json.dumps(jresponse, indent=4, sort_keys=True)
    
    writeFile(content=jsonPretty, folderPath=folderPath, fileName=fileName, filePath=None, mode='w', encoding="utf-8", loggingPrefix=locallogger.name)  






def writeFile(content, folderPath=None, fileName=None, filePath=None, mode='w', encoding='utf-8', loggingPrefix=None, newline=None, setLogLevel=None, logFileWriteConfirmation=True):
    if loggingPrefix == None:
        locallogger = logging.getLogger(f'{__name__}.writeFile')
    else:
        locallogger = logging.getLogger(f'{loggingPrefix}.{__name__}.writeFile')
        
    
    if setLogLevel != None:
        core.adjustLogLevel(loggerName=locallogger.name, logLevel=setLogLevel)
        
    
    
    if filePath == None:
        if (folderPath != None) and (fileName != None):
            filePath = os.path.join(folderPath, fileName)
        else:
            locallogger.error(f"folderPath, filePath and fileName are None.")
            sys.exit(1)
    openAndWriteFailed = True
    openAndWriteFailedNum = 0
    while (openAndWriteFailed):
        try:
            if mode in ['r', 'w', 'r+', 'w+', 'rw']:
                with open(filePath, mode, encoding=encoding, newline=newline) as file:
                    file.write(content)
                    openAndWriteFailed = False
            elif mode in ['rb', 'wb', 'rwb']:
                with open(filePath, mode, newline=newline) as file:
                    file.write(content)
                    openAndWriteFailed = False           
        except Exception:
            openAndWriteFailedNum = openAndWriteFailedNum + 1
            locallogger.exception(f"Exception happened. openAndWriteFailedNum = {openAndWriteFailedNum}")
            if (openAndWriteFailedNum >= 3):
                sys.exit(1)
    if logFileWriteConfirmation:
        locallogger.info(f"Content written to file at filePath {filePath}")
    return filePath




def prettyPrintColumns(df):
    columnList = list(df.columns)
    for column in columnList:
        print(f"        '{column}',")



pp = prettyPrintColumns


def prettyPrintColumnsForDictionary(df):
    columnList = list(df.columns)
    for column in columnList:
        print(f"        '{column}' : '',")    


pp2 = prettyPrintColumnsForDictionary


# class State():
#     def __init__(self, pathDict, stateName, locallogger, folderReference='Output_Folder'):
#         self.d = {}
#         self.name = stateName
#         self.filePath = os.path.join(pathDict[folderReference], f"State_Info_{stateName}.pickle")
#         self.locallogger = locallogger
#         self.getState()
#         self.locallogger.info(f"State file is at path: '{self.filePath}'")
#     def getStateName(self):
#         return self.name
#     def getState(self):
#         if not os.path.exists(self.filePath):
#             self.locallogger.info(f"No state information exists.")
#         else:
#             self.d = readPickleToObject(filePath=self.filePath)
#             self.locallogger.info(f"Loaded state information from file: '{self.filePath}'")
#     def save(self, showSaveLog=True):
#         writeObjectToPickle(objectValue=self.d, filePath=self.filePath, logInfoMessage=False)
#         if showSaveLog:
#             self.locallogger.info(f"Saved state information to file: '{self.filePath}'")
#     def delete(self):
#         self.locallogger.info(f"Deleting State...!")
#         self.d = {}
#         self.save()  
#     # Gets Old value if existing, if not, it sets
#     def getSet(self, key, value, showSaveLog=True):
#         if key in self.d.keys():
#             return self.d[key]
#         else:
#             self.d[key] = value
#             self.save(showSaveLog)
#             return self.d[key]
#     def update(self, key, value, showSaveLog=True):
#         self.d[key] = value
#         self.save(showSaveLog)  
#     def get(self, key):
#         return self.d[key]
#     def clear(self, key):
#         if key in self.d.keys():
#             del self.d[key]

#%% ==================================================== Improved State Class ======================================



class State():
    def __init__(self, pathDict, locallogger, folderReference='Output_Folder'):
        self.d = {}
        self.metadataList = []
        self.folderReference = folderReference
        self.metadataFilePath = os.path.join(pathDict[self.folderReference], f"State_Metadata.pickle")
        self.locallogger = locallogger
        self.pathDict = pathDict
        self.getState()
        self.saveMetadata()
    
    def getState(self):
        if not os.path.exists(self.metadataFilePath):
            self.locallogger.info(f"No state information exists.")
        else:
            self.metadataList = readPickleToObject(filePath=self.metadataFilePath)
            for key in self.metadataList:
                valueObjectFilePath = os.path.join(self.pathDict[self.folderReference], f"State_{key}.pickle")
                if not os.path.exists(valueObjectFilePath):
                    self.d[key] = None
                else:
                    self.d[key] = readPickleToObject(filePath=valueObjectFilePath)
    
    def saveMetadata(self, showSaveLog=False):
        writeObjectToPickle(objectValue=self.metadataList, filePath=self.metadataFilePath, logInfoMessage=False)
        if showSaveLog:
            self.locallogger.info(f"Saved Metadata State information to file: '{self.metadataFilePath}'")



    def save(self, key, showSaveLog=False):
        valueObjectFilePath = os.path.join(self.pathDict[self.folderReference], f"State_{key}.pickle")
        writeObjectToPickle(objectValue=self.d[key], filePath=valueObjectFilePath, logInfoMessage=False)
        if showSaveLog:
            self.locallogger.info(f"Saved {key} State information to file: '{valueObjectFilePath}'")
    
    def delete(self, key):
        if key in self.d.keys():
            del self.d[key]
            self.metadataList.remove(key)
            self.saveMetadata()
            valueObjectFilePath = os.path.join(self.pathDict[self.folderReference], f"State_{key}.pickle")
            os.unlink(valueObjectFilePath)

    
    # Gets Old value if existing, if not, it sets
    def getSet(self, key, value, showSaveLog=False):
        if key not in self.metadataList:
            self.metadataList.append(key)
            self.saveMetadata()
        if key in self.d.keys():
            return self.d[key]
        else:
            self.d[key] = value
            self.save(key=key, showSaveLog=showSaveLog)
            return self.d[key]
    
    def update(self, key, value, showSaveLog=False):
        if key not in self.metadataList:
            self.metadataList.append(key)
            self.saveMetadata()
        self.d[key] = value
        self.save(key=key, showSaveLog=showSaveLog)
    
    def get(self, key):
        return self.d[key]




# class State():
#     def __init__(self, stateName, pathDict, locallogger, folderReference='Output_Folder'):
#         self.d = {}
#         self.metadataList = []
#         self.stateName = stateName
#         self.folderReference = folderReference
#         self.metadataFilePath = os.path.join(pathDict[self.folderReference], f"State_{self.stateName}_Metadata.pickle")
#         self.locallogger = locallogger
#         self.pathDict = pathDict
#         self.getState()
#         self.saveMetadata()
    
#     def getState(self):
#         if not os.path.exists(self.metadataFilePath):
#             self.locallogger.info(f"No state information exists.")
#         else:
#             self.metadataList = readPickleToObject(filePath=self.metadataFilePath)
#             for key in self.metadataList:
#                 valueObjectFilePath = os.path.join(self.pathDict[self.folderReference], f"State_{self.stateName}_{key}.pickle")
#                 self.d[key] = readPickleToObject(filePath=valueObjectFilePath)
    
#     def saveMetadata(self, showSaveLog=False):
#         tempFilePath = f"{self.metadataFilePath}_temp"
#         realFilePath = self.metadataFilePath
#         writeObjectToPickle(objectValue=self.metadataList, filePath=tempFilePath, logInfoMessage=False)
#         tempObject = readPickleToObject(filePath=tempFilePath, showLog=False)
#         if self.metadataList == tempObject:
#             # os.replace(tempFilePath, realFilePath)
#             shutil.copyfile(tempFilePath, realFilePath)
#         else:
#             self.locallogger.error(f"Pickle write error!")
#             sys.exit(1)
#         if showSaveLog:
#             self.locallogger.info(f"Saved Metadata State information to file: '{self.metadataFilePath}'")



#     def save(self, key, showSaveLog=False):
#         valueObjectFilePath = os.path.join(self.pathDict[self.folderReference], f"State_{self.stateName}_{key}.pickle")
#         tempFilePath = f"{valueObjectFilePath}_temp"
#         realFilePath = valueObjectFilePath
#         writeObjectToPickle(objectValue=self.d[key], filePath=tempFilePath, logInfoMessage=False)
#         tempObject = readPickleToObject(filePath=tempFilePath, showLog=False)
#         flagEqual = False
#         if type(self.d[key]) in [pd.core.frame.DataFrame,]:
#             if self.d[key].shape == tempObject.shape:
#                 flagEqual = True
#         elif self.d[key] == tempObject:
#             flagEqual = True
#         if flagEqual:
#             # os.replace(tempFilePath, realFilePath)
#             shutil.copyfile(tempFilePath, realFilePath)
#         else:
#             self.locallogger.error(f"Pickle write error!")
#             sys.exit(1)
#         if showSaveLog:
#             self.locallogger.info(f"Saved {key} State information to file: '{valueObjectFilePath}'")
    
#     def delete(self, key):
#         if key in self.d.keys():
#             del self.d[key]
#             self.metadataList.remove(key)
#             self.saveMetadata()
#             valueObjectFilePath = os.path.join(self.pathDict[self.folderReference], f"State_{self.stateName}_{key}.pickle")
#             os.unlink(valueObjectFilePath)

    
#     # Gets Old value if existing, if not, it sets
#     def getSet(self, key, value, showSaveLog=False):
#         if key not in self.metadataList:
#             self.metadataList.append(key)
#             self.saveMetadata()
#         if key in self.d.keys():
#             return self.d[key]
#         else:
#             self.d[key] = value
#             self.save(key=key, showSaveLog=showSaveLog)
#             return self.d[key]
    
#     def update(self, key, value, showSaveLog=False):
#         if key not in self.metadataList:
#             self.metadataList.append(key)
#             self.saveMetadata()
#         self.d[key] = value
#         self.save(key=key, showSaveLog=showSaveLog)
    
#     def get(self, key):
#         return self.d[key]




# %% ================================================== Delete Items In Folder Older Than Date Time  =====================================================================================


def deleteItemsInFolderOlderThanDateTime(folderPath, thresholdDateTime, locallogger=None):
    epochThreshold = thresholdDateTime.timestamp()
    itemList = glob.glob(os.path.join(folderPath, "*"))
    dataList = []
    for itemPath in itemList:
        dictionary = {}
        dictionary["Item_Path"] = itemPath
        dictionary["Creation_Time_Epoch"] = os.stat(itemPath).st_ctime
        dataList.append(dictionary.copy())
    do_df = pd.DataFrame.from_dict(data=dataList, orient="columns")
    if len(do_df):
        filterframe = ( do_df["Creation_Time_Epoch"] < epochThreshold )
        selectedDf = do_df[filterframe]
        itemPathToDelete = list(selectedDf["Item_Path"])
        for itemPath in itemPathToDelete:
            try:
                os.unlink(itemPath)
            except Exception as e:
                if locallogger:
                    locallogger.error(e)
                    continue
                else:
                    raise e



def reArrangeItemsInList(allItemsList, itemsList, refItem=None, pasteAfter=True):
    reArrangedItemsList = []
    if refItem != None:
        for item in allItemsList:
            if (item != refItem) and (item not in itemsList):
                reArrangedItemsList.append(item)
            elif item == refItem:
                reArrangedItemsList.append(item)
                reArrangedItemsList = reArrangedItemsList + itemsList
            elif item in itemsList:
                pass
    else:
        reArrangedItemsList = itemsList
        for item in allItemsList:
            if item not in itemsList:
                reArrangedItemsList.append(item)
            elif item in itemsList:
                pass        

    return reArrangedItemsList
                


def moveColumns(df, columnsList, refColumn=None):
    locallogger = logging.getLogger(f"{__name__}.moveColumns")
    if (refColumn != None) and (refColumn not in list(df.columns)):
        locallogger.error(f"refColumn: '{refColumn}' not present in dataframe columns and refColumn is not None")
        sys.exit(1)
    allColumnList = df.columns
    reArrangedColumnsList = reArrangeItemsInList(allItemsList=allColumnList, itemsList=columnsList, refItem=refColumn)
    return df[reArrangedColumnsList]




def columnListExceptCertainOnes(df, exceptList):
    neededColumnsList = [x for x in df.columns if x not in exceptList]
    return neededColumnsList



def getColumnIfPresentList(df, columnList):
    columnPresentList = []
    allColumnsList = list(df.columns)
    for column in columnList:
        if column in allColumnsList:
            columnPresentList.append(column)
    return columnPresentList





def listCutIntoChunks(bigList, chunkSize):
    for i in range(0, len(bigList), chunkSize):
        yield bigList[i:(i+chunkSize)]
    

def cutIntoChunks(listOrDf, chunkSize):
    for i in range(0, len(listOrDf), chunkSize):
        yield listOrDf[i:(i+chunkSize)]







def mergeDataframes(dataframe1, dataframe2, onColumns_Left, onColumns_Right, howMerge='left', ensureNoDuplicatesOnRightForLeftMerge=False, replaceNullValuesInOutput=False):
    locallogger = logging.getLogger(f"{__name__}.mergeDataframes")
    
    if ((howMerge == 'left') and (ensureNoDuplicatesOnRightForLeftMerge)):
        dataframe2 = dropDuplicates(df=dataframe2, list_of_column_to_determine_uniqueness=onColumns_Right)
    locallogger.debug(f"Before Merge: dataframe1.shape: {dataframe1.shape}, dataframe2.shape: {dataframe2.shape}")
    dataframe3 = dataframe1.merge(dataframe2, how=howMerge, left_on=onColumns_Left, right_on=onColumns_Right)
    if replaceNullValuesInOutput:
        dataframe3 = replaceNullValuesInDataframe(dataframe3)
    locallogger.debug(f"After Merge: dataframe3.shape: {dataframe3.shape}")
    # Detecting _x columns, as this usually implies names with same columns existing on left and right data.  
    columnList = list(dataframe3.columns)
    for column in columnList:
        if column.endswith("_x"):
            locallogger.error(f"Column ending with _x detected after merge.  Please rectify logic!  Column Name: '{column}'")
            sys.exit(1)
    return dataframe3




def dropDuplicates(df, list_of_column_to_determine_uniqueness=None):
    df = df.copy()
    locallogger = logging.getLogger(f"{__name__}.dropDuplicates")
    
    if type(df) == pd.core.series.Series:
        df = df.to_frame()
    #locallogger.debug(f"Duplicates: {(df[df[list_of_column_to_determine_uniqueness].duplicated(keep=False)])}")
    locallogger.debug(f"Shape before dropping duplicates: {df.shape}")
    df = df.drop_duplicates(subset=list_of_column_to_determine_uniqueness, keep='first', inplace=False)
    df = df.reset_index(drop=True)
    locallogger.debug(f"Shape after dropping duplicates: {df.shape}")
    return df





