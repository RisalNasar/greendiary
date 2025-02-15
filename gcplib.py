
import os
import posixpath
import sys
from google.cloud import storage


from commonfunctions.core import getLocalLogger


bucketName = "bucket-te-1"


class GCPStorage:
    def __init__(self, pathDict, loggingPrefix=None):
        self.outputFolderRoot = pathDict['Output_Folder_Root']
    def getRemoteFilePath(self, localFilePath, loggingPrefix=None):
        locallogger = getLocalLogger(localloggername='GCPStorage.getStoragePath', rootFileName=__name__, loggingPrefix=loggingPrefix)
        self.locallogger = locallogger      
        lengthOfFolderRootString = len(self.outputFolderRoot)
        if not localFilePath.startswith(self.outputFolderRoot):
            locallogger.error(f"localFilePath '{localFilePath}' does not start with outputFolderRoot '{self.outputFolderRoot}'")
            sys.exit(1)
        remainingFilePath = localFilePath[lengthOfFolderRootString:]
        if os.name == 'nt':
            remainingFilePath = remainingFilePath.replace(os.sep, posixpath.sep)
        remoteFilePath = f"results{remainingFilePath}"
        return remoteFilePath
    def writeFile(self, localFilePath, loggingPrefix=None):
        locallogger = getLocalLogger(localloggername='GCPStorage.writeFile', rootFileName=__name__, loggingPrefix=loggingPrefix)
        storageClient = storage.Client()
        storageClient._http.verify = False
        bucket = storageClient.bucket(bucketName)
        remoteFilePath = self.getRemoteFilePath(localFilePath=localFilePath)
        blob = bucket.blob(remoteFilePath)
        blob.upload_from_filename(localFilePath)
        locallogger.info(f"Uploaded file to remote path: '{remoteFilePath}'")      




























