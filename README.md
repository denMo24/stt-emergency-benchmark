# stt-emergency-benchmark

This repository contains code and notebooks for evaluating speech-to-text (STT) systems in emergency-related scenarios.  
The focus lies on computing performance metrics such as **WER**, **medical-weighted WER (m-WER)**, **BLEU**, **semantic similarity**, and related statistical analyses.

No corpora, no audio data, no third-party models, and no lexical resources are distributed in this repository.

---

# Environment Setup

Each subfolder containing notebooks includes its own environment definitions:

- `environment.yml` – full Conda environment (all packages)
- `environment_minimal.yml` – minimal environment (only essential dependencies)

To create an environment:

```bash
# Full environment
conda env create -f environment.yml
```

```
# Minimal environment
conda env create -f environment_minimal.yml
```


Refer to the local README files inside submodules for additional details.


---


# Piper TTS Integration

This repository integrates Piper TTS, but **does not provide any Piper voice models**.

Some scripts reference Piper voice files (e.g., `.onnx`), but:

- models are **not included**
- they must be **downloaded separately**
- users must **check licensing** for each model individually

Official sources:

- https://github.com/rhasspy/piper
- https://github.com/OHF-Voice/piper1-gpl
- https://huggingface.co/rhasspy

---

# Medical WER (m-WER)

This project includes notebooks for computing:

- **m-WER** using user-provided medical lexica

## Important Notes

- No corpora, lexica, or medical term lists are included.
- The notebooks **only illustrate the methodology** for constructing such resources.
- All evaluation results in the repository are **aggregated metrics only**.

---

## Reproducibility

To reproduce m-WER or any evaluation steps, users must:

1. provide their own transcript data  
2. create or obtain their own lexica  
3. run the supplied notebooks  

The **methodology is documented**, but the **data and lexica are not distributed**.

---

# Audio, Corpora, and External Resources

This repository does **not** contain:

- audio recordings
- synonym tables  
- lexicon files  

Where external tools or models are referenced, **users must obtain them independently** and comply with their respective licenses.

---

# Code Ownership

All notebooks and scripts in this repository represent **our own implementation and methodology**.  
They do **not** include or redistribute external models, datasets, or corpora.

External resources referenced by the notebooks must be acquired and licensed **by the user**.


---

# MIT License

Copyright (c) 2025 
Nikola Stanic, Denis Moser, Murat Sariyar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included
   in all copies or substantial portions of the Software.

2. This license applies only to the original code written for this project.
   It does not apply to external models, audio files, corpora, lexica, or any
   third-party datasets referenced by the code or notebooks.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
