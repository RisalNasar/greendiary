# -*- coding: utf-8 -*-

import os
import posixpath
from azure.storage.blob import BlobClient
import logging
import sys
import tempfile
from pathlib import Path
import pandas as pd

import core


# containerName = "container1"





#%%

# Get Azure Data Lake File Path from Local File Path References


# def getAzureDataLakeFilePathFromLocalPathReferences(localFilePath):

#     # Extract out the path without the drive letter - For Windows machines
#     if localFilePath[1] == ':':
#         localFilePath2 = localFilePath[2:]
    
    
#     # For linux:
#     if localFilePath.startswith('/fileshare'):
#         localFilePath2 = localFilePath[10:]


#     filePathRemote = localFilePath2.replace(os.sep, posixpath.sep)
#     return filePathRemote




#%%


# def copyLocalFileToAzureDataLake(secretDict, localFilePath=None, localFolderPath=None, localFileName=None, loggingPrefix=None):
#     if loggingPrefix == None:
#         locallogger = logging.getLogger(f'{__name__}.copyLocalFileToAzureDataLake')
#     else:
#         locallogger = logging.getLogger(f'{loggingPrefix}.{__name__}.copyLocalFileToAzureDataLake')
        
#     connectionString = secretDict['AZURE_DATA_LAKE_DEV_1']
    
#     if localFilePath == None:
#         if (localFolderPath != None) and (localFileName != None):
#             localFilePath = os.path.join(localFolderPath, localFileName)
#         else:
#             locallogger.error(f"localFolderPath, localFilePath and localFileName are None.")
#             sys.exit(1)    



    
#     filePathRemote = getAzureDataLakeFilePathFromLocalPathReferences(localFilePath)
    
#     fileContent = commonfunctions.core.readFile(filePath=localFilePath, mode='rb',  loggingPrefix=None)
    
    
#     blob = BlobClient.from_connection_string(conn_str=connectionString, container_name=containerName, blob_name=filePathRemote)
    
#     uploadResponseDict = blob.upload_blob(data=fileContent, overwrite=True)
    
#     if 'last_modified' in uploadResponseDict.keys():
#         locallogger.info(f"Successfully wrote file to Azure Data Lake location: '{filePathRemote}'")
#     else:
#         locallogger.error(f"{uploadResponseDict}")
#         sys.exit(1)
    
#     return uploadResponseDict


#%%
    




#%%


# def copyTempFileToAzureDataLake(secretDict, tempFilePath, filePath=None, folderPath=None, fileName=None, loggingPrefix=None):
#     if loggingPrefix == None:
#         locallogger = logging.getLogger(f'{__name__}.copyTempFileToAzureDataLake')
#     else:
#         locallogger = logging.getLogger(f'{loggingPrefix}.{__name__}.copyTempFileToAzureDataLake')
        
#     connectionString = secretDict['AZURE_DATA_LAKE_DEV_1']
    
#     if filePath == None:
#         if (folderPath != None) and (fileName != None):
#             filePath = os.path.join(folderPath, fileName)
#         else:
#             locallogger.error(f"folderPath, filePath and fileName are None.")
#             sys.exit(1)    



    
#     filePathRemote = getAzureDataLakeFilePathFromLocalPathReferences(filePath)
    
#     fileContent = commonfunctions.core.readFile(filePath=tempFilePath, mode='rb',  loggingPrefix=None, logLevel='WARNING')
    
    
#     blob = BlobClient.from_connection_string(conn_str=connectionString, container_name=containerName, blob_name=filePathRemote)
    
#     uploadResponseDict = blob.upload_blob(data=fileContent, overwrite=True)
    
#     if 'last_modified' in uploadResponseDict.keys():
#         locallogger.info(f"Successfully wrote file to Azure Data Lake location: '{filePathRemote}'")
#     else:
#         locallogger.error(f"{uploadResponseDict}")
#         sys.exit(1)
    
#     return uploadResponseDict


#%%


# def writePickle(df, secretDict, folderPath=None, fileNamePrefix=None, filePath=None, loggingPrefix=None):
#     if loggingPrefix == None:
#         locallogger = logging.getLogger(f'{__name__}.writePickle')
#     else:
#         locallogger = logging.getLogger(f'{loggingPrefix}.{__name__}.writePickle') 
        
#     #commonfunctions.core.writePickle(df=df, folderPath=folderPath, fileNamePrefix=fileNamePrefix, filePath=filePath, loggingPrefix=loggingPrefix)
        
        
#     tempDir = tempfile.TemporaryDirectory()
#     commonfunctions.core.writePickle(df=df, folderPath=tempDir.name, fileNamePrefix='tempFile', loggingPrefix=loggingPrefix, logLevel='WARNING')
    
#     tempFilePath = os.path.join(tempDir.name, 'tempFile.pickle')
    
#     result = copyTempFileToAzureDataLake(secretDict=secretDict, tempFilePath=tempFilePath, filePath=filePath, folderPath=folderPath, fileName=f"{fileNamePrefix}.pickle", loggingPrefix=loggingPrefix)
    
#     tempDir.cleanup()
    
    
#     return result
    



#%%


class AzureDataLake:
    
    def __init__(self, secretDict, pathDict):
        if core.getParameter('ANALYTICS_CODE_MODE') == 'Production':
            self.connectionString = secretDict['AZURE_DATA_LAKE_PROD_1']
        else:
            self.connectionString = secretDict['AZURE_DATA_LAKE_DEV_1']
        self.outputFolderRoot = pathDict['Output_Folder_Root']
        self.containerName = "container1"
        
        
        suppressLogsList = [
            'azure.core.pipeline.policies.http_logging_policy',
            'urllib3.connectionpool',
            ]
        
        commonfunctions.core.setLoggerLevel(loggerNameList=suppressLogsList, loggingLevel=logging.WARNING)
        
    def getDataLakePath(self, localFilePath, loggingPrefix=None):
        locallogger = commonfunctions.core.getLocalLogger(localloggername='AzureDataLake.getDataLakePath', rootFileName=__name__, loggingPrefix=loggingPrefix)
        # Extract out the path without the drive letter - For Windows machines
        # if localFilePath[1] == ':':
        #     localFilePath2 = localFilePath[2:]
        # # For linux:
        # if localFilePath.startswith('/fileshare'):
        #     localFilePath2 = localFilePath[10:]
        
        lengthOfFolderRootString = len(self.outputFolderRoot)
        if not localFilePath.startswith(self.outputFolderRoot):
            locallogger.error(f"localFilePath '{localFilePath}' does not start with outputFolderRoot '{self.outputFolderRoot}'")
            sys.exit(1)
        remainingFilePath = localFilePath[lengthOfFolderRootString:]
        if os.name == 'nt':
            remainingFilePath = remainingFilePath.replace(os.sep, posixpath.sep)
        dataLakeFilePath = f"results{remainingFilePath}"
        return dataLakeFilePath
        
    def fileToDataLake(self, localFilePath, dataLakeFilePath, loggingPrefix=None):        
        locallogger = commonfunctions.core.getLocalLogger(localloggername='AzureDataLake.fileToDataLake', rootFileName=__name__, loggingPrefix=loggingPrefix)
        fileContent = commonfunctions.core.readFile(filePath=localFilePath, mode='rb',  loggingPrefix=None, logLevel='WARNING')
        blob = BlobClient.from_connection_string(conn_str=self.connectionString, container_name=self.containerName, blob_name=dataLakeFilePath)
        uploadResponseDict = blob.upload_blob(data=fileContent, overwrite=True)
        if 'last_modified' in uploadResponseDict.keys():
            locallogger.info(f"Successfully wrote file to Azure Data Lake location: '{dataLakeFilePath}'")
        else:
            locallogger.error(f"{uploadResponseDict}")
            sys.exit(1)
        return uploadResponseDict
    
    def pushFilesToDataLake(self, filePathList, loggingPrefix=None):
        locallogger = commonfunctions.core.getLocalLogger(localloggername='AzureDataLake.pushFilesToDataLake', rootFileName=__name__, loggingPrefix=loggingPrefix)
        responseDictList = []
        for filePath in filePathList:
            dataLakeFilePath = self.getDataLakePath(localFilePath=filePath, loggingPrefix=locallogger.name)
            responseDict = self.fileToDataLake(localFilePath=filePath, dataLakeFilePath=dataLakeFilePath, loggingPrefix=locallogger.name)
            responseDictList.append(responseDict)
        return responseDictList
            
    
    def fileFromDataLake(self, localFilePath, dataLakeFilePath, loggingPrefix=None, setLogLevel=None):
        locallogger = commonfunctions.core.getLocalLogger(localloggername='AzureDataLake.fileFromDataLake', rootFileName=__name__, loggingPrefix=loggingPrefix)
        if setLogLevel != None:
            commonfunctions.core.adjustLogLevel(loggerName=locallogger.name, logLevel=setLogLevel)
        blob = BlobClient.from_connection_string(conn_str=self.connectionString, container_name=self.containerName, blob_name=dataLakeFilePath)
        storageStreamDownloader = blob.download_blob()
        commonfunctions.core.writeFile(content=storageStreamDownloader.content_as_bytes(), filePath=localFilePath, mode='wb', loggingPrefix=locallogger.name, setLogLevel='WARNING')
        locallogger.info(f"Successfully wrote file from Azure Data Lake location to local path: '{localFilePath}'")
  
    
    def writePickle(self, df, folderPath=None, fileNamePrefix=None, filePath=None, loggingPrefix=None):
        locallogger = commonfunctions.core.getLocalLogger(localloggername='AzureDataLake.writePickle', rootFileName=__name__, loggingPrefix=loggingPrefix)
        tempDir = tempfile.TemporaryDirectory()
        commonfunctions.core.writePickle(df=df, folderPath=tempDir.name, fileNamePrefix='tempFile', loggingPrefix=loggingPrefix, logLevel='WARNING')
        tempFilePath = os.path.join(tempDir.name, 'tempFile.pickle')
        filePath = commonfunctions.core.getFilePath(filePath=filePath, folderPath=folderPath, fileName=f"{fileNamePrefix}.pickle", loggingPrefix=locallogger.name)
        dataLakeFilePath = self.getDataLakePath(localFilePath=filePath)
        result = self.fileToDataLake(localFilePath=tempFilePath, dataLakeFilePath=dataLakeFilePath, loggingPrefix=locallogger.name)
        tempDir.cleanup()
        #locallogger.info(f"Pickle Write to Azure Data Lake completed!")
        return result
    
    
    def readPickle(self, folderPath=None, fileNamePrefix=None, filePath=None, loggingPrefix=None):
        locallogger = commonfunctions.core.getLocalLogger(localloggername='AzureDataLake.readPickle', rootFileName=__name__, loggingPrefix=loggingPrefix)
        filePath = commonfunctions.core.getFilePath(filePath=filePath, folderPath=folderPath, fileName=f"{fileNamePrefix}.pickle", loggingPrefix=locallogger.name)
        dataLakeFilePath = self.getDataLakePath(localFilePath=filePath)
        tempDir = tempfile.TemporaryDirectory()
        tempFilePath = os.path.join(tempDir.name, 'tempFile.pickle')
        self.fileFromDataLake(localFilePath=tempFilePath, dataLakeFilePath=dataLakeFilePath, loggingPrefix=locallogger.name, setLogLevel='WARNING')
        filePathObject = Path(tempFilePath)
        if not filePathObject.is_file():
            locallogger.error(f"File does not exist: {tempFilePath}")
            sys.exit(1)
        df = pd.read_pickle(filePathObject)
        tempDir.cleanup()
        locallogger.info(f"Read pickle file from Azure Data Lake path: {dataLakeFilePath}")
        return df



#%%


































