# stt-emergency-benchmark

## Environment Setup

Each subfolder that contains code or notebooks also includes its own Conda environment specification files:

- `environment.yml` → full export of the original Conda environment (includes all installed packages).
- `environment_minimal.yml` → reduced version with only the essential dependencies needed to run the notebooks in this folder.

To recreate the environment, you can use:

```bash
# Full environment
conda env create -f environment.yml

# Minimal environment
conda env create -f environment_minimal.yml


For more information look up the README-files in the respective files.
