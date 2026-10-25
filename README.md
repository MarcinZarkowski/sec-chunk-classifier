## Models trained:

[jinabert_small](https://huggingface.co/MarcinZarkowski/stonky_sec_jinabert_small)
[modernbert](https://huggingface.co/MarcinZarkowski/modernbert-sec-classifier)



## AWS SageMaker Setup Instructions

Run these exact commands in your SageMaker terminal to install `uv`, create the environment, and link it to the Jupyter Notebook.

### 1. Clean Cache (If Disk is Full)
SageMaker instances have small default hard drives. If you run out of space installing PyTorch, either increase your EBS Volume size in the SageMaker settings to 50GB, or run:
```bash
uv cache clean
```

### 2. Install `uv` and Sync Dependencies
```bash
# Install astral uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to path
source $HOME/.local/bin/env

# Create .venv and install all pyproject.toml dependencies instantly
uv sync
```

### 3. Register the Jupyter Kernel
```bash
# Activate the environment
source .venv/bin/activate

# Install the kernel so the Notebook UI can see it
python -m ipykernel install --user --name=sec-chunk-env --display-name "Python (sec-chunk)"
```

### 4. Run the Notebook
1. Open `training_notebook.ipynb` in the SageMaker UI.
2. Click the Kernel name in the top right (e.g., "Python 3").
3. Select **Python (sec-chunk)** from the dropdown list.
4. Run all cells to start training the model on the GPU!


