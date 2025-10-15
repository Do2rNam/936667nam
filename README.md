[![CI](https://github.com/cuong062/cuong062/actions/workflows/ci.yml/badge.svg)](https://github.com/cuong062/cuong062/actions/workflows/ci.yml)

# Fruit Detector (camera) + SQLite info lookup

This is a small Python demo that:

- Opens your webcam and detects common fruits using simple color/shape heuristics (banana, apple, orange) using OpenCV.
- After detection it queries a local SQLite database for nutritional information and displays it.

Requirements
- Python 3.8+
- Install dependencies from `requirements.txt`

Quick start (PowerShell):

```powershell

python -m venv .venv
.\.venv\Scripts\Activate.ps1


pip install -r requirements.txt


python -m pytest -q


python app.py
```

How it works
- `app.py` captures frames from the default camera, runs a heuristic detector in `detector.py` and when a fruit is detected queries `fruits.db` via `db.py`.

Notes
- This is a demo using simple heuristics — for production use consider a trained ML model (TensorFlow/PyTorch) for higher accuracy.
- If you don't need the camera, the `test_detector.py` file contains synthetic tests for `detect_fruit` that don't require physical hardware.
