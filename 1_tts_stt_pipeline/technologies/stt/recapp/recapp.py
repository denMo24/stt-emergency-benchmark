from utils.setup_helper import SetupHelper
from utils.mongodb_handler import MongoDBHandler
import os
import subprocess
import json
import time
from enum import Enum
from pathlib import Path

class TTSRecapp:
    class TranscriptionStatus:
        # Enum for Status on Request Sending
        class SentStatus(Enum):
            DELIVERED = 1
            FAILED = 2
        
        # Enum for Status on Recapp servers (Job Transcription Status)
        class ServerStatus(Enum):
            PENDING = 1
            RUNNING = 2
            DONE = 3
            REJECTED = 4
            DELETED = 5
            EXPIRED = 6
            
        class DownloadStatus(Enum):
            NOT_STARTED = 1
            COMPLETED = 2
            FAILED = 3

    CONST_ERROR_HTTP_RESULT = "Error in processing404"
    
    def __init__(self):
        """Initialize TTS Recapp by loading the config file and establishing a MongoDB Connection
        """
        recapp_setup = SetupHelper("tts_recapp", os.getcwd())
        self.recapp_config = recapp_setup.getConfigValues()
        self.mongodb_handler = MongoDBHandler(self.recapp_config, "recapp")
        self.api = self.recapp_config['api']
        self.token = self.recapp_config['token']
        self.model = self.recapp_config['model']
    
    def __del__(self):
        """Destructor
        """
        self.mongodb_handler.disconnectMongoDB()
    
    def checkIfFileProcessed(self):
        """To Check, which files have not been processed by the server.
        """
        query = {
            "sentStatus": self.TranscriptionStatus.SentStatus.DELIVERED.value, 
            "serverStatus": self.TranscriptionStatus.ServerStatus.REJECTED.value
            }
        allRejectedRequests = list(self.mongodb_handler.searchByQuery(query))
        
        for dialog_file in Path(self.getSourceFolderPath()).iterdir():
            if dialog_file.is_file() and dialog_file.suffix.lower() == ".wav":
                file = str(os.path.basename(dialog_file))
                found = False
                for item in allRejectedRequests:
                    itemName = str(item["fileName"])
                    if (file == itemName):
                        found = True
                if found:
                    print(f"Item found in DB for {file}")
                else:
                    print(f"INFO: No Item found in DB for {file}")
                        
    def checkForUpdatesOnServer(self):
        """Check if there are any Updates on the Recapp Server
        """
        # Checking for items in MongoDB if the Server Status is still pending
        query = {
            "sentStatus": self.TranscriptionStatus.SentStatus.DELIVERED.value, 
            "serverStatus": {"$in": 
                [self.TranscriptionStatus.ServerStatus.PENDING.value,
                 self.TranscriptionStatus.ServerStatus.RUNNING.value]
                }
            }
        allUnfinishedRequests = self.mongodb_handler.searchByQuery(query)
        serverJobs = self.getAllJobsOnServer("jobs")
        allJobsOnServer = json.loads(serverJobs)
        
        for request in allUnfinishedRequests:
            for serverJob in allJobsOnServer:
                # Matching DB Object with JobList from Server
                if request["taskID"] == serverJob["id"]:
                    print (f"Checking for new Server status on Task {request["taskID"]}")
                    match serverJob["status"]:
                        case "running": 
                            newvalue = {'$set': {'serverStatus': self.TranscriptionStatus.ServerStatus.RUNNING.value}}
                        case "done": 
                            newvalue = {'$set': {'serverStatus': self.TranscriptionStatus.ServerStatus.DONE.value}}
                        case "rejected":
                            newvalue = {'$set': {'serverStatus': self.TranscriptionStatus.ServerStatus.REJECTED.value}}
                        case _: return
                    print ("Setting new serverStatus")
                    self.mongodb_handler.updateItem({'taskID': request["taskID"]}, newvalue)
    
    def checkForPendingTranscriptDownload (self):
        """Check on the Recapp server if there are any pending transcript downloads
        """
        query = {
            "serverStatus": self.TranscriptionStatus.ServerStatus.DONE.value,
            "downloadStatus": self.TranscriptionStatus.DownloadStatus.NOT_STARTED.value
            }
        allPendingDownloads = self.mongodb_handler.searchByQuery(query)
        for pendingDownloadItem in allPendingDownloads:
            self.getTranscriptFromTask("jobs", pendingDownloadItem["taskID"])
            time.sleep(1)
    
    def sendCurlCommand(self, command):
        """Send a curl command

        Args:
            command (str): Command to be sent.

        Returns:
            str: Result from the HTTP-Query or None
        """
        try:
            # Run the curl command and capture the output
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            http_code = result.stdout[-3:]
            print(f"HTTP-Response Code: {http_code}")
            # If the request is successful, return the response body
            if self.isSuccessHTTPCode(http_code):
                return result.stdout
            else:
                return None
        except subprocess.CalledProcessError as e:
            # If there's an error, return the error message
            print(f"Error: {e.stderr}")
            return self.CONST_ERROR_HTTP_RESULT

        except Exception as e:
            # Handle any other exceptions
            print(f"An unexpected error occurred: {str(e)}")
            return self.CONST_ERROR_HTTP_RESULT
        
    def sendTranscripitionTask(self, pathToAudioFile: str, apiEndpoint: str):
        """Send Transcription Task to Recapp and save request in MongoDB for tracking

        Args:
            pathToAudioFile (str): Path to audio file
            apiEndpoint (str): API-Endpoint

        Returns:
            Any: HTTP-Response
        """
        # Construct the curl command
        curl_command = [
            "curl", 
            "-X", "POST",  # GET or POST
            f"{self.api}/{apiEndpoint}",  # URL
            "-H", "accept: */*",
            "-H", f"Authorization: Bearer {self.token}",  # Headers
            "-H", "Content-Type: multipart/form-data",  # Headers
            "-F", f"data_file=@{pathToAudioFile};type=audio/mpeg",
            "-F", f"language={self.model}",
            "-F", "additional_vocab=[]",
            "-F", "priority=",
            "-w", "%{http_code}"
        ]
        res = self.sendCurlCommand(curl_command)
        
        # Extract Conversation ID to add to DB
        convoID, ambient, volume = self.getProcessedFileInfo(pathToAudioFile)
        http_code = res[-3:]
        if (self.isSuccessHTTPCode(http_code)):
            reqID = self.getRecappRequestID(res[:-3])
        else:
            reqID = self.CONST_ERROR_HTTP_RESULT
        newItem = self.createNewRecappRequestBody(reqID, os.path.basename(pathToAudioFile), convoID, ambient, volume)
        self.mongodb_handler.addNewItem(newItem)
        return res
        
    def getTranscriptionStatus (self, apiEndpoint: str, taskID: str):
        """Check the status of a specific job and update it in mongoDB if it changed.

        Args:
            apiEndpoint (str): API-Endpoint
            taskID (str): Task ID

        Returns:
            Any: HTTP-Response
        """
        # Construct the curl command
        curl_command = [
            "curl", 
            "-X", "GET", 
            f"{self.api}/{apiEndpoint}/{taskID}",  # URL
            "-H", "accept: application/json",
            "-H", f"Authorization: Bearer {self.token}",  # Headers
            "-w", "%{http_code}"
        ]
        res = self.sendCurlCommand(curl_command)
        if not (res == self.CONST_ERROR_HTTP_RESULT or res == None):
            data = json.loads(res[:-3])
            match data["status"]:
                case "queued": newvalue = {'$set': {'serverStatus': self.TranscriptionStatus.ServerStatus.PENDING.value}}
                case "running": newvalue = {'$set': {'serverStatus': self.TranscriptionStatus.ServerStatus.RUNNING.value}}
                case "done": newvalue = {'$set': {'serverStatus': self.TranscriptionStatus.ServerStatus.DONE.value}}
                case _: return
            self.mongodb_handler.updateItem({'taskID': taskID}, newvalue)
        return res
    
    def getAllJobsOnServer (self, apiEndpoint: str):
        """Get a list of all jobs on the Recapp server

        Args:
            apiEndpoint (str): API-Endpoint

        Returns:
            Any: List of all requests on the server
        """
        # Construct the curl command
        curl_command = [
            "curl", 
            "-X", "GET", 
            f"{self.api}/{apiEndpoint}",  # URL
            "-H", "accept: application/json",
            "-H", f"Authorization: Bearer {self.token}",  # Headers
            "-w", "%{http_code}"
        ]
        res = self.sendCurlCommand(curl_command)
        return res[:-3]
          
    def getTranscriptFromTask(self, apiEndpoint: str, taskID: str):
        """Update the Request-Object in MongoDB with the Transcript if its done.

        Args:
            apiEndpoint (str): Endpoint for API
            taskID (str): Task ID on Server

        Returns:
            Any: HTTP-Response
        """
        # Construct the curl command
        curl_command = [
            "curl", 
            "-X", "GET", 
            f"{self.api}/{apiEndpoint}/{taskID}/transcript",  # URL
            "-H", "accept: application/json",
            "-H", f"Authorization: Bearer {self.token}",  # Headers
            "-w", "%{http_code}"
        ]
        res = self.sendCurlCommand(curl_command)
        if not (res == self.CONST_ERROR_HTTP_RESULT or res == None):
            # Prepare item in DB to be updated
            newvalues = {
                '$set': {
                    'rawTranscriptData': res[:-3],
                    'downloadStatus': self.TranscriptionStatus.DownloadStatus.COMPLETED.value
                }
            }
            self.mongodb_handler.updateItem({'taskID': taskID}, newvalues)
        return res

    def createNewRecappRequestBody(self, taskID: str, fileName: str, convo: str, ambient: str, volume: str):
        """_summary_

        Args:
            taskID (str): Task ID
            fileName (str): Filename of processed file
            convo (str): Conversation ID
            ambient (str): Which ambient has been used?
            volume (str): What volume was the ambient in?

        Returns:
            dict: Object for MongoDB
        """
        print(f"Creating new Object for {taskID}")
        serverStatus = self.TranscriptionStatus.ServerStatus.PENDING.value
        downloadStatus = self.TranscriptionStatus.DownloadStatus.NOT_STARTED.value
        if (taskID == self.CONST_ERROR_HTTP_RESULT):
            sentStatus = self.TranscriptionStatus.SentStatus.FAILED.value
        else:
            sentStatus = self.TranscriptionStatus.SentStatus.DELIVERED.value
        recapp_request_template = {
            "taskID": taskID, # Holds the ID for the TaskID on the Recapp Server
            "fileName": fileName, # Filename
            "convoID": convo, # Holds the ID of the conversation, which is processed
            "ambientVariant": ambient, # What ambient version it this layered with
            "processedVolume": volume, # what adjusted ambient volume is contained
            "sentStatus": sentStatus, # Status if the request has been received
            "serverStatus": serverStatus, # Status on the server, if the transcription has been processed already
            "downloadStatus": downloadStatus, # Has the transcription already been downloaded and processed locally.
            "rawTranscriptData": "" # Raw Data for Transcript from Response Body
        }
        return recapp_request_template
    
    def getProcessedFileInfo (self, filePath: str):
        """Returns the file info embedded in the filename for processing

        Args:
            filePath (str): File Path to processed file.

        Returns:
            str: Returns ConversationID, what kind of ambient it's layered with and it's volume.
        """
        parts = os.path.basename(filePath).split('_')
        volPart = parts[2].split('.')
        return parts[0], parts[1], volPart[0]
    
    def getRecappRequestID (self, requestBody: str):
        """Get Request ID from server

        Args:
            requestBody (str): Response from HTTP-Request

        Returns:
            Any: RequestID
        """
        res_json = json.loads(requestBody)
        return res_json.get("id")
    
    def getSourceFolderPath(self):
        """Return Source Directory Path

        Returns:
            str: Source Directory Path
        """
        return self.recapp_config['source_dir']
    
    def isSuccessHTTPCode(self, HTTP_code):
        """Check if HTTP-Code is Success

        Args:
            HTTP_code (Any): HTTP-Code from response

        Returns:
            Bool: Is Sucess Code
        """
        return 200 <= int(HTTP_code) < 300
    
    def mergeRecappTranscript(self, rawData: list):
        """Merge all single word transcriptions into a whole text (ignoring the speaker)

        Args:
            rawData (list): List of all Words in text.

        Returns:
            str: Merged text.
        """
        mergedText = ""
        
        # JSON is split into Word Chucks, so we iterate through it
        for wordChunk in rawData["results"]:
            # We take element 0, because it's a list of sets
            wordMetadata = wordChunk["alternatives"][0]
            spokenWord = wordMetadata["content"]
            mergedText += f"{spokenWord} "
        return mergedText[:-1]
    
    def transferTranscriptsFilesToMongoDB (self):
        """Transfer all requests from the requests collection to the transcription collection
        """
        allRequests = list(self.mongodb_handler.getAllItems())
        # Pointing MongoDB Handler to new DB and Collection to transfer Transcripts
        self.mongodb_handler.setDB(self.recapp_config['transcript_db'])
        self.mongodb_handler.setCollection(self.recapp_config['transcript_collection'])
        for req in allRequests:
            newObject = self.createNewRecappMongoDBObject(req)
            self.mongodb_handler.addNewItem(newObject)

    def createNewRecappMongoDBObject (self, requestbody):
        """Converting HTML-Response to MongoDB Object

        Args:
            requestbody (Any): unedited Request-body

        Returns:
            dict: Object for MongoDB
        """
        rawData = json.loads(requestbody["rawTranscriptData"])
        transcript_template = {
            "technology": "recapp", #which technology has been used
            "model": self.model, # which model has been used
            "fileName": requestbody["fileName"], # Filename
            "convoID": requestbody["convoID"], # Holds the ID of the conversation, which is processed
            "ambientVariant": requestbody["ambientVariant"], # What ambient version it this layered with
            "processedVolume": requestbody["processedVolume"], # what adjusted ambient volume is contained
            "text": self.mergeRecappTranscript(rawData),
            "rawTranscriptData": requestbody["rawTranscriptData"] # Raw Data for Transcript from Response Body
        }
        return transcript_template