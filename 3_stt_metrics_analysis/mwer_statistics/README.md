## Medical WER Calculation

This repository provides two complementary notebooks:

### 1. `building_mwer.ipynb` (optional)
- Purpose: builds auxiliary resources such as token-level error lists (`wer_token_sources.json`, substitution/deletion/insertion CSVs).
- Usage: only needed if you want to inspect or regenerate detailed error corpora.
- Not required for reproducing the main statistical results.

### 2. `mwer_calculate.ipynb` (main)
- Purpose: computes **standard WER** and **medical-weighted WER (m-WER)** at the phrase level.
- Inputs:
  - MongoDB transcripts collection (`src_wer_denis` = reference, `text_wer_denis` = hypothesis).
  - Medical lexica:
    - `lexikon_cleaned_ger_synonyms.csv`
    - `lexikon_ATC-Bedeutung_final_noarticles.csv`
    - `lexikon_deDE15LinguisticVariant_final_noarticles.csv`
- Output:
  - `transcripts_wer_mwer_phrase.csv`  
    (includes `wer, S, D, I, S_med, D_med, I_med, mwer` for each transcript).

### Reproducibility
For reproducing the results in the paper, it is sufficient to run **`mwer_calculate.ipynb`**.  
The resulting file `transcripts_wer_mwer_phrase.csv` is the dataset used for all statistical analyses.