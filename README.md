# Nirmaan AI – Spoken Introduction Scorer

Rubric-driven, Explainable Evaluation Engine for Student Self-Introductions.

This project evaluates a student's spoken introduction (transcript) using a structured rule-based rubric. It provides transparent scoring, detailed breakdowns, and a simple Streamlit UI for demonstration.

## Features

- Fully rule-based scoring engine
- Explainable evaluation aligned with rubric criteria
- 0–100 overall scoring + detailed JSON breakdown
- Streamlit web interface
- Colab notebook for reproducible demonstration
- Modular and extendable codebase

## Evaluation Criteria

### 1. Salutation (0–5)
Advanced greeting > Standard greeting > No greeting.

### 2. Must-Have Information (0–20)
Name, Age, Class, School, Hobbies/Goals.

### 3. Good-To-Have Details (0–10)
Family, Origin, Thanks, School highlights, Extracurricular.

### 4. Flow / Structure (0–5)
Greeting → Name → Basics → Family/Origin → Goals.

### 5. Speech Rate (0–10)
Based on WPM if duration provided.

### 6. Vocabulary Richness (0–10)
Type–Token Ratio (TTR).

### 7. Clarity (0–15)
Filler words per 100 words.

### 8. Engagement / Positivity (0–15)
Positive vs negative word ratios.

## Output Format

Example:
```
{
  "overall_score": 86.3,
  "criteria": [...],
  "meta": { "word_count": 92, "duration_seconds": 55 }
}
```

## Local Setup

```
conda create -n nirmaan_intro python=3.10
conda activate nirmaan_intro
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deployment (Render/Railway)

Build:
```
pip install -r requirements.txt
```

Start:
```
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```

## Project Structure

```
scoring.py
streamlit_app.py
requirements.txt
README.md
DEPLOYMENT.md
LICENSE
architecture-diagram.png
github-banner.png
Nirmaan_Intro_Scorer_Colab_short.ipynb
Case study for interns.xlsx
Sample text for case study.txt
```

## License
MIT License
