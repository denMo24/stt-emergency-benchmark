# SpeechBrain RescueSpeech Transcription

This workflow uses the **speechbrain/whisper_rescuespeech** model to transcribe `.wav` files and store results in MongoDB.  

## Installation
- Create the Conda environment using the provided `.yml` file with all dependencies.  

## Workflow
1. **Initial pipeline**  
   Run `1_tt_stt_pipeline` → fills MongoDB with the baseline transcripts (without SpeechBrain).  

2. **SpeechBrain transcription**  
   In folder `2_stt_speechbrain_only`, run `1_stt-pipe-whisper-rescuespeech.ipynb` → produces per-audio JSON transcription files using speechbrain. Our results are in folder "results_speechbrain".

3. **Import into MongoDB**  
   Run `2_preprocess_import_to_mongodb.ipynb` → loads the generated JSON results into MongoDB, in a new collection `transcripts_denis`.  

## Parameters
- Change `notebook_dir` in the script to point to your audio files.  
- Optionally adjust `num_files` (default: 2000, `None` = all files).  
- Output JSON files are saved in a timestamped `results_...` folder inside `notebook_dir`.  
- Each JSON file can then be imported into MongoDB.  

## Note
On **June 24, 2025** the original Hugging Face config caused errors with `bos_index` / `eos_index`. Therefore, the YAML was adapted. Please refer to the provided file at `whisper_rescuespeech/hyperparams.yaml`.  
