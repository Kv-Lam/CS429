# LLMaestro

A UTK COSC429 research project investigating whether chord notation systems affect LLM generation of chord progressions. Two notation formats are compared — **Harte** (`C:maj`) and **ABC** (`[C E G]`) — by fine-tuning GPT-2 on each and evaluating the generated progressions using Jensen-Shannon Divergence and n-gram novelty.

> **Disclaimer:** The `results.ipynb` notebook was developed with the assistance of Claude Code (claude.ai/code).

---

## Prerequisites

- Python 3.8+
- A [Hugging Face](https://huggingface.co) account and access token (for pushing fine-tuned models)
- Git

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd fp
```

### 2. Download the ChoCo dataset

Download `v1.0.0.zip` from the [ChoCo releases page](https://github.com/smashub/choco/releases/tag/v1.0.0), place it in the project root, and unzip it:

```bash
unzip v1.0.0.zip
```

This should produce a `v1.0.0/` directory containing the JAMS files.

### 3. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install jams transformers torch matplotlib numpy
```

---

## Reproducing the Results

Run the following steps in order:

### Step 1 — Convert JAMS files to Harte notation JSON

Reads JAMS files from `v1.0.0/` and writes one JSON per song to `data/Harte/`.

```bash
python harte.py
```

### Step 2 — Convert Harte JSON to ABC notation JSON

Reads `data/Harte/` and writes ABC-notation equivalents to `data/ABC/`.

```bash
python harte_to_abc_dict.py
```

### Step 3 — Flatten JSON files into training text files

Converts both `data/Harte/` and `data/ABC/` into flat text files (`train_harte.txt` / `train_abc.txt`) with delimiter tokens `<|title|>`, `<|key|>`, `<|chords|>`, and `<|endoftext|>`.

```bash
python convert_chords.py
```

### Step 4 — Fine-tune GPT-2

Trains GPT-2 for 5 epochs on one of the flat text files. Toggle between Harte and ABC by editing the `fine_tune(...)` call at the bottom of `train.py`. The trained model is pushed to Hugging Face under `CS429/<output_name>` and loss/perplexity plots are saved to `results/<output_name>/`.

```bash
python train.py
```

Run this twice (once per notation) to produce both `CS429/gpt2-harte` and `CS429/gpt2-abc`.

### Step 5 — Evaluate and visualize results

Open the notebooks to run experiments and inspect results:

```bash
jupyter notebook main.ipynb       # primary experiment: generate and evaluate progressions
jupyter notebook results.ipynb    # results visualization and analysis
jupyter notebook count.ipynb      # chord count / distribution analysis
```

---

## Project Structure

```
fp/
├── harte.py                # JAMS → Harte JSON (data/Harte/)
├── harte_to_abc_dict.py    # Harte JSON → ABC JSON (data/ABC/)
├── convert_chords.py       # JSON → train_harte.txt / train_abc.txt
├── train.py                # Fine-tune GPT-2; push to Hugging Face
├── evaluations.py          # JSD and n-gram novelty metrics
├── main.ipynb              # Primary experiment notebook
├── results.ipynb           # Results visualization (built with Claude Code)
├── count.ipynb             # Chord distribution analysis
├── data/
│   ├── Harte/              # Per-song Harte JSON files
│   └── ABC/                # Per-song ABC JSON files
└── v1.0.0/                 # ChoCo JAMS files (downloaded separately)
```

---

## Evaluation Metrics

- **Jensen-Shannon Divergence (JSD):** Measures how closely the chord distribution of a generated progression matches the training corpus (both converted to Roman numerals for key-agnostic comparison). Lower is better.
- **N-gram Novelty:** Fraction of 4-grams in the generated progression that do not appear in the training data. Higher means more creative output.

---

## Dataset

[ChoCo v1.0.0](https://github.com/smashub/choco/releases/tag/v1.0.0) — Billboard subset (~890 songs) annotated with Harte chord notation.
