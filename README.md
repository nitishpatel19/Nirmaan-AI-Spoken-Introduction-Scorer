
# 🎤 Nirmaan AI — Spoken Introduction Scorer

Rubric-driven, explainable evaluation engine for student self-introductions.

## What this project does (Hinglish)

- Student ka **spoken intro** (audio) ko transcript mana gaya hai.
- Yeh tool **sirf transcript text** le kar:
  - salutation / greeting check karta hai,
  - important info (name, class, hobbies, goals, family, origin...) detect karta hai,
  - flow sahi order me hai ya nahi dekhata hai,
  - filler words count karta hai,
  - vocabulary richness (type–token ratio) nikalta hai,
  - positivity / engagement estimate karta hai,
  - aur in sab ko combine karke **0–100 score** deta hai
    + detailed breakdown JSON ke form me.

Isse interviewer ko clearly dikhega ki scoring **transparent** hai aur rubric se linked hai.

## Tech overview

- **Core logic**: `scoring.py` → function `evaluate_transcript(transcript, duration_seconds=None)`
- **UI**: `streamlit_app.py` (simple web app for demo)
- **Rubric**: inspired by `Case study for interns.xlsx` (Nirmaan file)

## Input & Output

### Input

```python
from scoring import evaluate_transcript

result = evaluate_transcript(
    transcript="Good morning, my name is ...",
    duration_seconds=55,  # optional
)
```

### Output

```python
{
  "overall_score": 86.3,
  "max_score": 100.0,
  "criteria": [
    {
      "name": "Salutation quality",
      "max_score": 5,
      "score": 4,
      "details": {...},
      "score_normalized_0_1": 0.8
    },
    ...
  ],
  "meta": {
    "word_count": 92,
    "duration_seconds": 55,
    "raw_total": 77.5,
    "raw_max": 90.0
  }
}
```

## How scoring works (summary)

1. **Salutation (0–5)** – `Hi/Hello` / `Good morning` / advanced phrases.
2. **Core details (0–20)** – name, age, class, school, hobbies/goals.
3. **Good-to-have (0–10)** – family, origin city, thanks, extracurricular, etc.
4. **Flow (0–5)** – rough order: greeting → name → basics → family/origin → hobbies/goals.
5. **Speech rate (0–10)** – uses word-count + `duration_seconds` → WPM buckets (optional).
6. **Vocabulary richness (0–10)** – Type–Token Ratio → rubric buckets.
7. **Clarity (0–15)** – filler words per 100 words.
8. **Engagement (0–15)** – positive vs negative word hits → positivity index.

Raw total is scaled to **0–100** for easier interpretation.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open the URL shown in your terminal (usually `http://localhost:8501`).

## Deploy (Render / Railway style)

- **Build command**

```bash
pip install -r requirements.txt
```

- **Run command**

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```

## Files

- `scoring.py` – core scoring logic
- `streamlit_app.py` – Streamlit UI
- `requirements.txt` – dependencies
- `README.md` – this document
- `DEPLOYMENT.md` – detailed deployment steps
- `LICENSE` – MIT license
- `github-banner.png` – repo header image
- `architecture-diagram.png` – simple architecture diagram
- `Nirmaan_Intro_Scorer_Colab_short.ipynb` – Colab version
- `Case study for interns.xlsx` – original rubric (given)
- `Sample text for case study.txt` – sample transcript (given)
- `Nirmaan AI intern Case study instructions.pdf` – problem statement (given)
