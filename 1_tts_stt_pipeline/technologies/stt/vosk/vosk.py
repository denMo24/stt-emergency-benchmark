import subprocess
from utils.setup_helper import SetupHelper
import os
import json
from vosk import Model, KaldiRecognizer
from pathlib import Path
from utils.mongodb_handler import MongoDBHandler

class TTSVosk: 
    def __init__(self):
        """Initialize TTSVosk by loading the config file
        """
        vosk_setup = SetupHelper("tts_vosk", os.getcwd())
        self.vosk_config = vosk_setup.getConfigValues()
        self.mongodb_handler = MongoDBHandler(self.vosk_config, "vosk")
        self.CONST_MODEL = "vosk-model-de-0.21"
        self.CONST_MODEL_PATH = os.path.join(os.getcwd(), self.getModelSourcePath(), self.CONST_MODEL)
        self.CONST_SAMPLERATE = 16000
        
    def transcribeFiles(self):
        """Transcribe all files in the given source folder
        """
        # Sort Files alphabetically
        src = Path(self.getSourceDirectory())
        src_sorted = sorted(src.iterdir(), key=lambda x: x.name)
        
        # Setup Output Folder
        modelOutput = os.path.join(self.getOutputDirectory(), self.CONST_MODEL)
        if not Path(modelOutput).exists():
            print(f"Model-Folder not found. Creating Folder '{self.CONST_MODEL}' at {self.getOutputDirectory()}.")
            Path(modelOutput).mkdir(parents=True, exist_ok=True)
            
        # Load Model
        model = Model (self.CONST_MODEL_PATH)
        
        # Initialize recognizer with the model
        recognizer = KaldiRecognizer(model, self.CONST_SAMPLERATE)  # Assuming the audio is 16kHz
        
        for file in src_sorted:
            print (f"Transcribing file: {file}")
            # Prepare Outputfile
            fileName = file.stem
            saveFile = "vosk_" + self.CONST_MODEL + "_" + fileName + ".json"
            savePath = os.path.join(modelOutput, saveFile)
            transcription = self.transcribe(file, model, recognizer)
            print(f"Saving transcript to file at {savePath}")
            with open(savePath, 'w') as f:
                json.dump(transcription, f, indent=4)
            f.close()
    
    def transcribe(self, file, model: Model, recognizer: KaldiRecognizer):
        """Transcribe the given audio file

        Args:
            file (str): Path to Audio file to be transcribed
            model (Model): Loaded Vosk Model
            recognizer (KaldiRecognizer): Loaded KaldiRecognizer for Transcription

        Returns:
            list: List of transcribed text chunks
        """
        # Save all snippets in this list
        all_transcriptions = []
        # Extract audio from the input file and pipe it to Vosk
        with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
            file,
            "-ar", str(self.CONST_SAMPLERATE) , "-ac", "1", "-f", "s16le", "-"],
            stdout=subprocess.PIPE) as process:
            
            # Read Data
            while True:
                # Read audio frame
                partial_data = process.stdout.read(4000)  # Size of the audio chunks to process
                
                if len(partial_data) == 0:
                    break
                # Pass the audio data to the recognizer
                if recognizer.AcceptWaveform(partial_data):
                    result = recognizer.Result()
                    decoded_result = json.loads(result)
                    all_transcriptions.append(decoded_result)
        recognizer.FinalResult()
        recognizer.Reset()
        return all_transcriptions
    
    def transferJSONFilesToMongoDB (self):
        """Transferring the generated JSON-Files to the MongoDB Instance
        """
        # Get subfolders in Output directory to iterate through
        subfolders = [subfolder for subfolder in os.listdir(self.getOutputDirectory()) if os.path.isdir(os.path.join(self.getOutputDirectory(), subfolder))]
        print(f"subdolders: {subfolders}")
        for sf in subfolders:
            sf_path = os.path.join(self.getOutputDirectory(), sf)
            print(f"sf_path: {sf_path}")
            for file in os.listdir(sf_path):
                file_info = file.split("_")
                file_path = os.path.join(sf_path, file)
                with open (file_path, "r") as f:
                    file_data = json.load(f)
                newObject = self.createNewRecappMongoDBObject(file,file_info, file_data)
                print(f"adding new item: {sf_path}")
                self.mongodb_handler.addNewItem(newObject)
                f.close()
    
    def mergeVoskTranscript(self, rawData: list):
        """Merge all single line chunks into one text.

        Args:
            rawData (list): List of all transcribed text chunks

        Returns:
            str: merged text
        """
        mergedText = ""
        
        # JSON is split into Word Chucks, so we iterate through it
        for transcribedSentence in rawData:
            # We take element 0, because it's a list of sets
            text = transcribedSentence["text"]
            mergedText += f"{text} "
        return mergedText[:-1]
    
    def createNewRecappMongoDBObject (self, fileName, fileinfo, rawdata):
        """Creating a MongoDB Object for Vosk 

        Args:
            fileName (Any): Filename
            fileinfo (Any): File Metadata from filename
            transcript (Any): Transcribed text
            rawdata (Any): raw JSON data

        Returns:
            dict: Object for MongoDB
        """
        volume = fileinfo[4].split(".")
        transcript_template = {
            "technology": fileinfo[0], #which technology has been used
            "model": fileinfo[1], # which model has been used
            "fileName": fileName, # Filename
            "convoID": fileinfo[2], # Holds the ID of the conversation, which is processed
            "ambientVariant": fileinfo[3], # What ambient version it this layered with
            "processedVolume": volume[0], # what adjusted ambient volume is contained
            "text": self.mergeVoskTranscript(rawdata),
            "rawTranscriptData": rawdata # Raw Data for Transcript from Response Body
        }
        return transcript_template
    
    def getSourceDirectory(self):
        """Return Source Directory Path

        Returns:
            str: Source Directory Path
        """
        return self.vosk_config['source_dir']
    
    def getOutputDirectory(self):
        """Return Output Directory Path

        Returns:
            str: Output Directory Path
        """
        return self.vosk_config['output_dir']
    
    def getModelSourcePath (self):
        """Return Vosk Model Path

        Returns:
            str: Vosk model Path
        """
        return self.vosk_config['model_path']
    
    def getTTSWhisperConfig(self):
        """Return Vosk Config

        Returns:
            dict: Vosk Config
        """
        return self.vosk_config