
# Deployment – Nirmaan AI Intro Scorer

## Local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open `http://localhost:8501`.

## Render / Railway (summary)

1. Push repo to GitHub.
2. Create **Web Service**.
3. Set:

**Build command**

```bash
pip install -r requirements.txt
```

**Start command**

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```

4. Deploy and use public URL in submission.
