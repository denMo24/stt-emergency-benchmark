from utils.setup_helper import SetupHelper
from utils.mongodb_handler import MongoDBHandler
import os
import json
import whisper
from pathlib import Path
import torch

class TTSWhisper:
    def __init__(self):
        """Initialize TTS Whisper by loading the config file
        """
        whisper_setup = SetupHelper("tts_whisper", os.getcwd())
        self.whisper_config = whisper_setup.getConfigValues()
        self.mongodb_handler = MongoDBHandler(self.whisper_config, "whisper")
        
    def transcribeFiles(self, model, device, language):
        """Transcribe all files with the given model

        Args:
            model (Any): Whisper Model
            device (Any): CUDA Device or CPU
            language (Any): What language is the text
        """
        whisp_model = whisper.load_model(model, device=device)
        modelOutput = os.path.join(self.getOutputDirectory(), model)
        
        # Sort Files alphabetically
        src = Path(self.getSourceDirectory())
        src_sorted = sorted(src.iterdir(), key=lambda x: x.name)
        
        # Setup Output Folder
        if not Path(modelOutput).exists():
            print(f"Model-Folder not found. Creating Folder '{model}' at {self.getOutputDirectory()}.")
            Path(modelOutput).mkdir(parents=True, exist_ok=True)
        
        for file in src_sorted:
            print (f"Transcribing file: {file}")
            # Prepare Outputfile
            fileName = file.stem
            saveFile = "whisper_" + model + "_" + fileName + ".json"
            savePath = os.path.join(modelOutput, saveFile)
            # Start transcription
            with torch.cuda.device(device):
                result = whisp_model.transcribe(str(file), language=language, fp16=False)
            jsonResult = json.dumps(result, indent=4)
            print(f"Saving transcript to file at {savePath}")
            with open(savePath, 'w') as f:
                f.write(jsonResult)
            f.close()
            
    def transferJSONFilesToMongoDB (self):
        """Transferring the generated JSON-Files to the MongoDB Instance
        """
        # Get subfolders in Output directory to iterate through
        subfolders = [subfolder for subfolder in os.listdir(self.getOutputDirectory()) if os.path.isdir(os.path.join(self.getOutputDirectory(), subfolder))]
        for sf in subfolders:
            sf_path = os.path.join(self.getOutputDirectory(), sf)
            for file in os.listdir(sf_path):
                file_info = file.split("_")
                file_path = os.path.join(sf_path, file)
                with open (file_path, "r") as f:
                    file_data = json.load(f)
                newObject = self.createNewWhisperMongoDBObject(file,file_info, file_data["text"], file_data)
                print(f"adding new item: {newObject}")
                self.mongodb_handler.addNewItem(newObject)
                f.close()

    def createNewWhisperMongoDBObject (self, fileName, fileinfo, transcript, rawdata):
        """Creating a MongoDB Object for Whisper 

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
            "text": transcript,
            "rawTranscriptData": rawdata # Raw Data for Transcript from Response Body
        }
        return transcript_template
    
    def getSourceDirectory(self):
        """Return Source Directory Path

        Returns:
            str: Source Directory Path
        """
        return self.whisper_config['source_dir']
    
    def getOutputDirectory(self):
        """Return Output Directory Path

        Returns:
            str: Output Directory Path
        """
        return self.whisper_config['output_dir']
    
    def getTTSWhisperConfig(self):
        """Return Whisper Config

        Returns:
            dict: Whisper Config
        """
        return self.whisper_config