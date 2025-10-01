# MongoDB Export: `transcripts_denis`

### MongoDB Dump (split into parts)

The MongoDB dump `transcripts_denis_dump.zip` was split into multiple parts (<100 MB each) to comply with GitHub’s file size limit.

To reconstruct the original file, run the following in the folder `mongodb/`:

```bash
cat transcripts_denis_dump.zip.part_* > transcripts_denis_dump.zip
```

Then extract it:

```bash
unzip transcripts_denis_dump.zip
```



---


This folder contains the MongoDB collection **`transcriptions.transcripts_denis`**, exported as a zipped dump (`transcripts_denis.zip`).  
It is provided for reproducibility of the STT benchmarking experiments.

---

## Collection Structure

| Key               | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `_id`             | Unique MongoDB document identifier                                          |
| `convoID`         | Audio file ID (can repeat, as each file was run through multiple STT models)|
| `srcText`         | Original utterance text (synthetically generated, used for TTS audio)       |
| `text`            | Raw STT output of the respective model                                      |
| `src_meer_denis`  | Normalized version of `srcText` (for m-WER analysis)                        |
| `text_meer_denis` | Normalized version of `text` (for m-WER analysis)                           |
| `model`           | Model identifier used for transcription                                    |
| `technology`      | STT system family (e.g., Whisper, Vosk, Recapp)                            |
| `ambientVariant`  | Background noise type inserted                                |
| `processedVolume` | Loudness level (dBFS) at which the audio was mixed with noise              |

---

## Audio Files

The corresponding synthetic audio files consist of approx. **2,000 files** (> **70 GB**).  
These are not included in the repository.  

➡️ They can be regenerated locally using the **TTS pipeline**.  
See instructions in [**`1_tts_stt_pipeline/README.md`**](../1_tts_stt_pipeline/README.md).

Or per request (denis.moser@bfh.ch).

---

## Restore Instructions

To import the collection into your own MongoDB instance:

```bash
unzip transcripts_denis.zip -d dump_tmp
mongorestore --uri="mongodb://localhost:27018/" dump_tmp/


## Important Notes

Several resources are not provided in this repository and must be obtained separately:

OpenAI API key (required for semantic similarity and embedding-based metrics)

Recapp URL and API key (required for usage of the proprietary Recapp STT model)

Original source data for building lookup tables (must be downloaded from the respective providers and handled according to their license terms)
However, we provide the lookup tables as intermediate artifacts in the respective metric subfolders, so that results can be reproduced without re-downloading the original resources.


