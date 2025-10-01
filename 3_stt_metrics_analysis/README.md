# STT Metrics Analysis

This folder contains all analyses of **speech-to-text (STT) system performance** under noisy emergency medical dialogue conditions.  
Each subfolder corresponds to one evaluation metric and includes the full processing chain.

---

## Structure

- **Metric subfolders** (e.g., `bleu/`, `lex_statistics/`, `wer/`):
  - **Notebooks**: end-to-end computation of the metric.
  - **Intermediate artifacts**: preprocessing outputs and helper files needed for the calculation.
  - **Results**: final CSVs with metric scores per transcript/system/environment.
  - **Statistical analysis**: descriptive stats, plots, and hypothesis tests.

- **Preprocessing utilities**  
  Shared scripts and helper notebooks to normalize transcripts, tokenize, or prepare lexica.

---

## Requirements

- Standard Python scientific stack:
  - `pandas`, `numpy`, `matplotlib`, `scipy`, `sklearn`, `jiwer` (for WER), etc.
- MongoDB access to the provided `transcripts_denis` collection.
- **For semantic similarity**:
  - An **OpenAI API key** is required (e.g. for embeddings).  
    Set your key as an environment variable before running:
    ```bash
    export OPENAI_API_KEY="your_key_here"
    ```
s
---

## Usage

1. Open the notebook for the metric of interest inside its folder.
2. Run all cells to reproduce preprocessing, metric calculation, and statistical analysis.
3. Final result tables (e.g., `*_results.csv`) are stored alongside the notebooks and are the basis for the plots and statistics reported in the paper.

---

## Outputs

- Each metric produces:
  - **Transcript-level results** (per convo/system/condition).
  - **Aggregated statistics** (mean, std, CI).
  - **Plots** used in the paper.

The outputs from these notebooks are directly used in the **Results & Discussion** sections of the manuscript.
