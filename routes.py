"""
Flask routes for the Crop Disease Prediction App.
Handles:
  GET  /               → landing page
  GET  /analyze        → disease analysis page
  POST /api/predict    → runs CNN + QCNN and returns JSON comparison
"""

import os
import time
import tempfile
from flask import render_template, request, jsonify

from models.model_loader import (
    SimpleCNN, RobustQCNN, load_model, predict,
    NUM_CLASSES, CLASS_NAMES,
    CNN_TEMPERATURE, QCNN_TEMPERATURE
)

# ──────────────────────────────────────────────────────────────
# Model checkpoint paths
# Place your .pth files inside the  models/  folder
# ──────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
CNN_PATH   = os.path.join(BASE_DIR, "models", "best_simple_cnn_20260310_163919.pth")
QCNN_PATH  = os.path.join(BASE_DIR, "models", "best_quantum_cnn_20260310_164916.pth")

# ──────────────────────────────────────────────────────────────
# Load models once at startup
# ──────────────────────────────────────────────────────────────
_cnn_model  = SimpleCNN(NUM_CLASSES)
_qcnn_model = RobustQCNN(NUM_CLASSES)

_cnn_model,  cnn_ok,  cnn_msg  = load_model(_cnn_model,  CNN_PATH)
_qcnn_model, qcnn_ok, qcnn_msg = load_model(_qcnn_model, QCNN_PATH)

print(f"[ModelLoader] CNN  → {'✅ loaded' if cnn_ok  else '❌ ' + cnn_msg}")
print(f"[ModelLoader] QCNN → {'✅ loaded' if qcnn_ok else '❌ ' + qcnn_msg}")

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# ──────────────────────────────────────────────────────────────
# Disease metadata  — recommendations per predicted class
# ──────────────────────────────────────────────────────────────
DISEASE_INFO = {
    "healthy": {
        "status": "healthy",
        "tips": [
            "Continue current maintenance practices",
            "Monitor for early signs of discoloration",
            "Ensure consistent irrigation schedule",
            "Consider soil nutrient testing every 3–4 weeks",
        ],
    },
    "bacterial_spot": {
        "status": "diseased",
        "tips": [
            "Apply copper-based bactericide immediately",
            "Remove and destroy heavily affected leaves",
            "Avoid overhead watering — use drip irrigation",
            "Disinfect tools between plants to prevent spread",
        ],
    },
    "early_blight": {
        "status": "diseased",
        "tips": [
            "Apply chlorothalonil or mancozeb fungicide",
            "Remove lower infected leaves promptly",
            "Mulch around base to reduce soil splash",
            "Rotate crops next season — avoid same family",
        ],
    },
    "late_blight": {
        "status": "diseased",
        "tips": [
            "Apply systemic fungicide (metalaxyl) immediately",
            "Remove and bag all infected tissue — do not compost",
            "Improve air circulation between plants",
            "Harvest unaffected tubers/fruits early if severe",
        ],
    },
    "default": {
        "status": "unknown",
        "tips": [
            "Isolate affected plants from healthy ones",
            "Consult a local agricultural extension service",
            "Photograph progression over 2–3 days",
            "Test soil pH and nutrient levels",
        ],
    },
}


def get_disease_info(label: str) -> dict:
    label_lower = label.lower()
    for key in DISEASE_INFO:
        if key in label_lower:
            return DISEASE_INFO[key]
    return DISEASE_INFO["default"]


def format_label(raw: str) -> str:
    """
    Pepper__bell___Bacterial_spot  -> Pepper Bell -- Bacterial Spot
    Pepper__bell___healthy         -> Pepper Bell -- Healthy
    Potato___Early_blight          -> Potato -- Early Blight
    Potato___Late_blight           -> Potato -- Late Blight
    Potato___healthy               -> Potato -- Healthy
    """
    if "___" in raw:
        idx     = raw.index("___")
        plant   = raw[:idx].replace("__", " ").replace("_", " ").strip().title()
        disease = raw[idx+3:].replace("_", " ").strip().title()
        return f"{plant} — {disease}"
    return raw.replace("_", " ").title()


# ──────────────────────────────────────────────────────────────
# REGISTER ROUTES
# ──────────────────────────────────────────────────────────────
def register_routes(app):

    @app.route("/")
    def landing():
        return render_template("landing.html")

    @app.route("/analyze")
    def analyze_page():
        return render_template("analyze.html")

    @app.route("/compare")
    def compare_page():
        return render_template("compare.html")

    # ── API: predict with both models ──────────────────────────
    @app.route("/api/predict", methods=["POST"])
    def api_predict():
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400

        # Save to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        file.save(tmp.name)
        tmp.close()

        results = {}

        try:
            # ── CNN prediction ──
            if cnn_ok:
                t0 = time.perf_counter()
                cnn_label, cnn_conf, cnn_top5 = predict(tmp.name, _cnn_model, temperature=CNN_TEMPERATURE)
                cnn_time = round((time.perf_counter() - t0) * 1000, 1)  # ms
                results["cnn"] = {
                    "label":      cnn_label,
                    "display":    format_label(cnn_label),
                    "confidence": round(cnn_conf * 100, 2),
                    "top5":       [(format_label(l), round(p * 100, 2)) for l, p in cnn_top5],
                    "time_ms":    cnn_time,
                    "loaded":     True,
                    "params":     _cnn_model.count_parameters(),
                    **get_disease_info(cnn_label),
                }
            else:
                results["cnn"] = {"loaded": False, "error": cnn_msg}

            # ── QCNN prediction ──
            if qcnn_ok:
                t0 = time.perf_counter()
                qcnn_label, qcnn_conf, qcnn_top5 = predict(tmp.name, _qcnn_model, temperature=QCNN_TEMPERATURE)
                qcnn_time = round((time.perf_counter() - t0) * 1000, 1)
                results["qcnn"] = {
                    "label":      qcnn_label,
                    "display":    format_label(qcnn_label),
                    "confidence": round(qcnn_conf * 100, 2),
                    "top5":       [(format_label(l), round(p * 100, 2)) for l, p in qcnn_top5],
                    "time_ms":    qcnn_time,
                    "loaded":     True,
                    "params":     _qcnn_model.count_parameters(),
                    **get_disease_info(qcnn_label),
                }
            else:
                results["qcnn"] = {"loaded": False, "error": qcnn_msg}

            # ── Agreement check ──
            if cnn_ok and qcnn_ok:
                results["agree"] = (cnn_label == qcnn_label)
                # Use QCNN as primary (higher capacity model)
                results["primary"] = "qcnn" if qcnn_ok else "cnn"

        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

        return jsonify(results), 200

    # ── Model status endpoint ──────────────────────────────────
    @app.route("/api/status")
    def api_status():
        return jsonify({
            "cnn":  {"loaded": cnn_ok,  "params": _cnn_model.count_parameters()  if cnn_ok  else 0, "msg": cnn_msg},
            "qcnn": {"loaded": qcnn_ok, "params": _qcnn_model.count_parameters() if qcnn_ok else 0, "msg": qcnn_msg},
            "classes": len(CLASS_NAMES),
        })
