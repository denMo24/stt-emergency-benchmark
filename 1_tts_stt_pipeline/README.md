# Evaluation Speech-To-Text Algorithms
## Description
This project lays out a evaluation pipeline to test different kinds of STT-Algorithms for their suitability of use in emergency situations. The project contains four main Jupyter-Notebooks, each representing a crucial step in this pipeline

1. Text-To-Speech with PiperTTS
2. Audio-Enhancing by adding background noises into the ambient layer to add authenticity
3. Transcription of the generated audio files

**Please note that this code doesn't support usage of the speechbrain model. To generate transcripts with speechbrain please use the code in "2_stt_speechbrain_only"!**


<img src="doc/project_visual.png" width="50%" />

## Installation
### Config-File
To use this repository, a config.ini file needs to be placed at the top layer of the repository. It needs to contain the following attributes:

```ini
[MongoDBDatabase]
db_name = -- Name of MongoDB Database, where the source texts are stored -- 
db_collection = -- Name of MongoDB Collection where source texts are stored --
db_host = -- URL of MongoDB Instance --
db_port = -- Port to be accessed on --

[MongoDBCollection]
collection_id = -- Identifier of the source texts --
collection_text = -- Column, where the texts are stored --

[Paths]
log_path = -- The Logger will save the .txt-Files on this path
audio_path = -- Where is the parent folder for the audios --

# Piper specific
piper_path = -- Parent folder of PiperTTS files --
piper_output_path = -- Output Path of Synthesized files --
piper_output_fullconversations_path = -- Output Path of merged audio files --

# Audio editing specific
audio_editing_output_path = -- Output Path of edited audio files -- 
ambient_source_path = -- Source Path of ambient files --

[Recapp]
url = -- URL to Recapp API --
token = --Access Token for Recapp API--
recapp_model = --Which model is to be used from Recapp--
recapp_db_name = -- Name of MongoDB Database to save requests --
recapp_req_collection = -- Name of MongoDB Collection where requests are saved --

[STTTranscriptions]
transcription_db_name = -- Name of MongoDB Database to save transcriptions into --
transcription_collection = -- Name of MongoDB Collection to save transcriptions into --
transcription_local_whisper = -- Path to local instance of transcriptions as files from whisper --
transcription_local_speechbrain = -- Path to local instance of transcriptions as files from SpeechBrain --
transcription_local_vosk = -- Path to local instance of transcriptions as files from Vosk --
vosk_model_path = -- Path to Model from Vosk to be used in transcription --
```

A copy of the .ini-File used in this project has been transferred to the BFH via a Hard Drive. To setup the virtual environments, consult the folder "venv", where you will find .yml-Files for each Jupyter Notebook. If you want to use them all in the same virtual environment, feel free to do so. 

To install these environments, run the following code in your conda terminal, replacing the filename:

```
conda env create -f environment.yml
```

<span style="color: red;font-weight: bold">Important</span>: Currently 1_TTS.ipynb only works on Windows, since a .exe-File is being used.

## Support
The author of this repository will not be reachable after finishing this project. A new support group has to be established to maintain this code for future use.

## Contributing
To contribute to this project, contact Murat Sariyar under murat.sariyar@bfh.ch from the BFH to get further details.

## Authors and acknowledgment
Authors:
- Nikola Stanic (stann1) - Student at Bern University of Applied Sciences

Ambient Sounds from:
- ZapSplat (https://www.ZapSplat.com)
- BBC Sound Effects (https://sound-effects.bbcrewind.co.uk/)

## License
### Non-Commercial License
This software is licensed under the GNU General Public License (GPL) v3. You are free to:

- **Share**: Copy and redistribute the material in any medium or format.
- **Adapt**: Remix, transform, and build upon the material.

However, this license is only for non-commercial purposes. You may not use, distribute, or modify this software for commercial purposes without obtaining a separate commercial license. For non-commercial use, you must adhere to the following terms:

- **Non-Commercial Use**: You may use, modify, and distribute the software for non-commercial purposes only. Commercial use (e.g., using the software for profit, in products, or services sold for profit) is prohibited under this license.
- **Attribution**: You must give appropriate credit to the original author(s), provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

### Commercial license
Contact authors to discuss further steps. ZapSplat needs to be contacted for use of their audio files in a commercial environment.