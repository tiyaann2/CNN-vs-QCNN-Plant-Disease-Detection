# 🌿 Agrisense — Complete Beginner Setup Guide

---

## What you have after unzipping

```
crop_disease_app/
├── app.py                                      ← Start the server (run this)
├── routes.py                                   ← URL routes + API logic
├── requirements.txt                            ← Python packages to install
├── models/
│   ├── model_loader.py                         ← Model architectures + load logic
│   ├── best_simple_cnn_20260310_163919.pth     ← ✅ Your trained CNN weights
│   └── best_quantum_cnn_20260310_164916.pth    ← ✅ Your trained QCNN weights
└── templates/
    ├── landing.html                            ← Home page
    ├── analyze.html                            ← Upload + predict page
    └── compare.html                            ← CNN vs QCNN dashboard
```

> ✅ The `.pth` model files are ALREADY inside the `models/` folder.
> You do NOT need to do anything with them — just follow the steps below.

---

## STEP 1 — Install Python

If you don't have Python installed:

1. Go to https://python.org/downloads
2. Download Python 3.11 or 3.12
3. During install on Windows: ✅ tick **"Add Python to PATH"**
4. Click Install

To check it worked, open a terminal and type:
```
python --version
```
You should see something like `Python 3.11.9`

---

## STEP 2 — Open a terminal in the project folder

**On Windows:**
1. Open File Explorer
2. Navigate into the `crop_disease_app` folder
3. Click the address bar at the top, type `cmd`, press Enter
   → A terminal opens already inside the folder ✅

**On Mac:**
1. Open Terminal (search "Terminal" in Spotlight)
2. Type `cd ` (with a space), then drag the `crop_disease_app` folder into the terminal
3. Press Enter

---

## STEP 3 — Create a virtual environment

A virtual environment keeps packages for this project separate from your system.

Type this in the terminal (copy exactly):

```
python -m venv venv
```

Then activate it:

**Windows:**
```
venv\Scripts\activate
```

**Mac / Linux:**
```
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal line. ✅

---

## STEP 4 — Install the required packages

```
pip install flask torch torchvision Pillow
```

This will take 2–5 minutes (PyTorch is large). You will see a lot of text scrolling — that is normal.

> ⚠️ **PennyLane note:** The QCNN model was trained with PennyLane but the
> server uses a lightweight simulation layer for inference — no PennyLane
> needed to run the web app. The model weights load correctly.

---

## STEP 5 — Run the app

```
python app.py
```

You should see:
```
[ModelLoader] CNN  → ✅ loaded
[ModelLoader] QCNN → ✅ loaded
 * Running on http://127.0.0.1:5000
```

---

## STEP 6 — Open the app in your browser

Open your browser and go to:
```
http://localhost:5000
```

You will see the Agrisense landing page. ✅

---

## Pages in the app

| URL | What it does |
|-----|-------------|
| `http://localhost:5000/` | Home / landing page |
| `http://localhost:5000/analyze` | Upload a leaf image → get CNN + QCNN predictions |
| `http://localhost:5000/compare` | Model comparison dashboard |

---

## How to use the Analyze page

1. Go to `http://localhost:5000/analyze`
2. Click **Browse Files** or drag a leaf photo onto the upload area
3. Click **Analyze with CNN & QCNN**
4. You will see:
   - The **primary result** (QCNN) with disease name + confidence %
   - Whether the models **agree or disagree**
   - Treatment recommendations
5. Click **"View CNN vs QCNN Comparison"** to expand the side-by-side detail
6. Go to `/compare` to see all your session predictions in a table + charts

---

## What the models can identify

These are the 5 disease classes the models were trained on:

| Class name | Meaning |
|------------|---------|
| `Pepper__bell___Bacterial_spot` | Pepper leaf with bacterial spot disease |
| `Pepper__bell___healthy` | Healthy pepper leaf |
| `Potato___Early_blight` | Potato leaf with early blight |
| `Potato___Late_blight` | Potato leaf with late blight |
| `Potato___healthy` | Healthy potato leaf |

> Upload images of **pepper or potato leaves** for best results.

---

## Troubleshooting

**"python is not recognized" (Windows)**
→ Reinstall Python and check the "Add to PATH" box during setup.

**"No module named flask"**
→ Make sure the virtual environment is active (you should see `(venv)` in terminal).
→ Run `pip install flask torch torchvision Pillow` again.

**"File not found: models/best_simple_cnn..."**
→ Make sure you are running `python app.py` from inside the `crop_disease_app` folder, not from a parent folder.

**Port 5000 already in use**
→ Change the last line of `app.py` to use a different port:
```python
app.run(debug=True, host="0.0.0.0", port=5001)
```
Then go to `http://localhost:5001`

**Models loaded but prediction looks wrong**
→ Make sure you are uploading images of **pepper or potato leaves** — the models were trained on only those 5 classes.

---

## To stop the app

Press **Ctrl + C** in the terminal.
