
from utils.setup_helper import SetupHelper
import os
import torch
from pathlib import Path
import json

from speechbrain.inference.separation import SepformerSeparation as Separator
from speechbrain.inference.ASR import WhisperASR

class TTSSpeechBrain:
    def __init__(self):
        """Initialize TTS SpeechBrain by loading the config file
        """
        speechbrain_setup = SetupHelper("tts_speechbrain", os.getcwd())
        self.speechbrain_config = speechbrain_setup.getConfigValues()
        
    def transcribeFiles (self, model, device, language):
        """Transcribe all files in the given source folder
        """
        # Load Model
        match model:
            case"noisy-whisper-rescuespeech":
                model["enh_model"] = Separator.from_hparams(
                    source="speechbrain/noisy-whisper-resucespeech", 
                    savedir='pretrained_models/noisy-whisper-rescuespeech',
                    hparams_file="enhance.yaml"
                )
                model["asr_model"] = WhisperASR.from_hparams(
                    source="speechbrain/noisy-whisper-resucespeech", 
                    savedir="pretrained_models/noisy-whisper-rescuespeech",
                    hparams_file="asr.yaml"
                )
            case "whisper_rescuespeech":
                model["asr_model"] = WhisperASR.from_hparams(
                    source="speechbrain/rescuespeech_whisper", 
                    savedir="pretrained_models/rescuespeech_whisper"
                )
            case _:
                print("no Matching Model-Handling found.")
                return
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
            saveFile = "speechbrain_" + model + "_" + fileName + ".json"
            savePath = os.path.join(modelOutput, saveFile)
            # Start Transcription
            transcription = self.transcribe(model, file, device)
            jsonResult = json.dumps(transcription, indent=4)
            print(f"Saving transcript to file at {savePath}")
            with open(savePath, 'w') as f:
                f.write(jsonResult)
            f.close()
                
    def transcribe (self, model: list, filePath, device):
        """Transcribe the given audio file

        Args:
            model (list): SpeechBrain Model
            filePath (Any): Path to Audio File
            device (Any): CUDA Device or CPU

        Returns:
            str: Transcribed Text
        """
        match model:
            case"noisy-whisper-rescuespeech":
                est_sources = Separator(model["enh_model"]).separate_file(path=filePath)
                pred_words, _ = WhisperASR(model["asr_model"])(est_sources[:, :, 0], torch.tensor([1.0]))
                return pred_words
            case "whisper_rescuespeech":
                transcript = WhisperASR(model["asr_model"]).transcribe_file(filePath)
                return transcript
            case _:
                print("no Matching Model-Handling found.")
                
    def getSourceDirectory(self):
        """Return Source Directory Path

        Returns:
            str: Source Directory Path
        """
        return self.speechbrain_config['source_dir']
    
    def getOutputDirectory(self):
        """Return Output Directory Path

        Returns:
            str: Output Directory Path
        """
        return self.speechbrain_config['output_dir']
    
    def getTTSWhisperConfig(self):
        """Return Whisper Config

        Returns:
            dict: Whisper Config
        """
        return self.speechbrain_config