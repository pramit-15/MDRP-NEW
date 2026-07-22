import time
import traceback as _tb
from flask import Blueprint, request, jsonify, send_from_directory, current_app

from backend.app.config import Config
from backend.utils.validators import validate_patient_data, validate_pdf_file
from backend.utils.exceptions import ValidationError, PDFParsingError, PredictionError
from backend.utils.logger import get_logger
from backend.auth.decorators import login_required
from backend.services.history_service import history_service
from predict import predict_all
from backend.utils.pdf_parser import extract_with_gemini, extract_with_regex, sanity_check

logger = get_logger("api_routes")

# Blueprint for versioned API
api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
# Blueprint for root routes (index + backward compatibility)
root_bp = Blueprint('root', __name__)

_DEBUG = Config.MDRP_DEBUG

# ─────────────────────────────────────────────────────────────────────────────
# Root endpoints (Backward Compatibility)
# ─────────────────────────────────────────────────────────────────────────────

@root_bp.route("/")
def index():
    return send_from_directory(current_app.config['TEMPLATES_DIR'], "index.html")

@root_bp.route("/predict", methods=["POST"])
def predict_legacy():
    return _predict_logic()

@root_bp.route("/parse-pdf", methods=["POST"])
def parse_pdf_legacy():
    return _parse_pdf_logic()


# ─────────────────────────────────────────────────────────────────────────────
# V1 Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Returns application health status
    """
    from backend.app.factory import app_state
    uptime_sec = time.time() - app_state["start_time"]
    
    return jsonify({
        "status": "healthy",
        "models_loaded": app_state["models_loaded"],
        "version": app_state["version"],
        "uptime": round(uptime_sec, 2)
    }), 200


@api_bp.route("/ready", methods=["GET"])
def readiness_check():
    """
    Readiness check endpoint
    ---
    responses:
      200:
        description: API is ready to serve predictions
      503:
        description: API is not ready (models failed to load)
    """
    from backend.app.factory import app_state
    if app_state["models_loaded"]:
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "not_ready", "reason": "models_not_loaded"}), 503


@api_bp.route("/predict", methods=["POST"])
@login_required
def predict_v1():
    """
    Predict multiple disease risks
    ---
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer token from Clerk (e.g., "Bearer <token>")
      - in: body
        name: body
        required: true
        description: Patient data features
    responses:
      200:
        description: Risk prediction successful
      400:
        description: Validation Error
      401:
        description: Unauthorized
      500:
        description: Internal Server Error
    """
    return _predict_logic()


@api_bp.route("/parse-pdf", methods=["POST"])
@login_required
def parse_pdf_v1():
    """
    Extract lab values from PDF
    ---
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer token from Clerk (e.g., "Bearer <token>")
      - in: formData
        name: file
        type: file
        required: true
        description: Patient lab report PDF
    responses:
      200:
        description: Lab values extracted successfully
      400:
        description: Invalid PDF format
      401:
        description: Unauthorized
      500:
        description: Internal Server Error
    """
    return _parse_pdf_logic()


@api_bp.route("/history", methods=["GET"])
@login_required
def get_history_v1():
    """
    Get prediction history
    ---
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
      - in: query
        name: skip
        type: integer
        required: false
        default: 0
      - in: query
        name: limit
        type: integer
        required: false
        default: 10
    responses:
      200:
        description: List of predictions
    """
    from flask import g
    user_id = g.user.user_id
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    
    results, total = history_service.get_history(user_id, skip=skip, limit=limit)
            
    return jsonify({"items": results, "total": total, "skip": skip, "limit": limit}), 200


@api_bp.route("/history/<prediction_id>", methods=["GET"])
@login_required
def get_history_detail_v1(prediction_id):
    """
    Get prediction history details
    """
    from flask import g
    user_id = g.user.user_id
    
    result = history_service.get_history_detail(user_id, prediction_id)
    if not result:
        return jsonify({"error": "Not found"}), 404
        
    return jsonify(result), 200


@api_bp.route("/history/<prediction_id>", methods=["DELETE"])
@login_required
def delete_history_v1(prediction_id):
    """
    Delete prediction history
    """
    from flask import g
    user_id = g.user.user_id
    
    deleted = history_service.delete_history(user_id, prediction_id)
    if not deleted:
        return jsonify({"error": "Not found"}), 404
            
    return jsonify({"success": True}), 200

# ─────────────────────────────────────────────────────────────────────────────
# Implementation Logic
# ─────────────────────────────────────────────────────────────────────────────

def _predict_logic():
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            raise ValidationError("request", "No JSON body received or invalid JSON.")

        # Validate input with our centralized validators
        patient_data = validate_patient_data(data)

        start_time = time.time()
        # Proceed to prediction orchestration
        results = predict_all(patient_data)
        
        # --- Save Prediction to DB via Service ---
        from flask import g
        # Support cases without clerk middleware running or test environments
        user_id = getattr(g, "user", None) and g.user.user_id
        
        if user_id:
            try:
                prediction_id = history_service.save_prediction_result(user_id, results, patient_data)
                results["prediction_id"] = prediction_id
            except Exception as e:
                logger.error(f"Failed to persist prediction: {e}")
        # -----------------------------

        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Prediction completed in {duration_ms:.0f} ms | patient_id={patient_data.get('patient_id', 'N/A')}")

        return jsonify({
            "success":          True,
            "heart":            results["heart"],
            "diabetes":         results["diabetes"],
            "kidney":           results["kidney"],
            "bmi_used":         results.get("bmi_used", patient_data.get("bmi")),
            "scores_detail":    results.get("scores_detail", {}),
            "health_condition": results.get("health_condition", {}),
            "used_defaults":    results.get("used_defaults", []),
            "explainability":   results.get("explainability", {}),
            "prediction_id":    results.get("prediction_id"),
        })

    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": {
                "type": "ValidationError",
                "field": e.field,
                "message": e.message
            }
        }), 400
    except PredictionError as e:
        logger.exception("Prediction error in /predict")
        return jsonify({
            "success": False,
            "error": {
                "type": "PredictionError",
                "message": str(e)
            }
        }), 500
    except Exception as exc:
        logger.exception("Error in /predict")
        resp = {"success": False, "error": {"type": "SystemError", "message": str(exc)}}
        if current_app.config.get("MDRP_DEBUG"):
            resp["trace"] = _tb.format_exc()
        return jsonify(resp), 500


def _parse_pdf_logic():
    try:
        if "file" not in request.files:
            raise PDFParsingError("No file provided.")
            
        file = request.files["file"]
        validate_pdf_file(file)

        start_time = time.time()
        logger.info(f"Received PDF upload: {file.filename}")

        try:
            import pdfplumber
        except ImportError:
            return jsonify({"success": False,
                            "error": {"type": "ConfigurationError", "message": "pdfplumber not installed."}}), 500

        pdf_bytes = file.read()
        extracted, method = None, "regex"

        # ── Try Gemini first if GOOGLE_API_KEY is set ──────────────────────
        api_key = current_app.config.get("GOOGLE_API_KEY")
        if api_key:
            import io
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                raw_text = "\n".join(p.extract_text() or "" for p in pdf.pages)

            extracted = extract_with_gemini(raw_text, api_key)
            if extracted is not None:
                method = "gemini_ai"

        # ── Regex fallback ─────────────────────────────────────────────────
        if extracted is None:
            import io
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                raw_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            extracted = extract_with_regex(raw_text)
            method = "regex"

        cleaned = sanity_check(extracted)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"PDF parsed in {duration_ms:.0f} ms | filename={file.filename} | method={method} | fields_extracted={len(cleaned)}")

        return jsonify({
            "success":    True,
            "extracted":  cleaned,
            "count":      len(cleaned),
            "all_fields": list(cleaned.keys()),
            "method":     method,
        })

    except PDFParsingError as e:
        return jsonify({
            "success": False,
            "error": {
                "type": "PDFParsingError",
                "message": str(e)
            }
        }), 400
    except Exception as exc:
        logger.exception("Error in /parse-pdf")
        resp = {"success": False, "error": {"type": "SystemError", "message": f"PDF parse failed: {exc}"}}
        if current_app.config.get("MDRP_DEBUG"):
            resp["trace"] = _tb.format_exc()
        return jsonify(resp), 500
