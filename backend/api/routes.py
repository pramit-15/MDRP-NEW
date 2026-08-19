import time
import traceback as _tb
from flask import Blueprint, request, jsonify, send_from_directory, current_app, send_file

from backend.app.config import Config
from backend.utils.validators import validate_patient_data, validate_pdf_file
from backend.utils.exceptions import ValidationError, PDFParsingError, PredictionError
from backend.utils.logger import get_logger
from backend.auth.decorators import login_required
from backend.services.history_service import history_service
from backend.services.notification_service import notification_service
from backend.services.pdf_export_service import pdf_export_service
from backend.services.simulation_service import simulation_service
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

@root_bp.route("/simulate", methods=["POST"])
def simulate_legacy():
    return _simulate_logic()


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


@api_bp.route("/simulate", methods=["POST"])
def simulate_v1():
    """
    Interactive What-If lifestyle risk reduction simulation
    """
    return _simulate_logic()


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


@api_bp.route("/history/<prediction_id>/export-pdf", methods=["GET"])
@login_required
def export_history_pdf_v1(prediction_id):
    """
    Generate and download clinical PDF report for a prediction record
    """
    from flask import g
    user_id = g.user.user_id
    
    detail = history_service.get_history_detail(user_id, prediction_id)
    if not detail:
        return jsonify({"error": "Prediction record not found"}), 404
        
    try:
        pdf_buffer = pdf_export_service.generate_prediction_pdf(detail)
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"MDRP_Medical_Report_{prediction_id[:8]}.pdf"
        )
    except Exception as e:
        logger.exception(f"Failed to generate PDF for {prediction_id}: {e}")
        return jsonify({"error": "Failed to generate PDF report"}), 500


@api_bp.route("/notifications", methods=["GET"])
@login_required
def get_notifications_v1():
    """
    Get in-app notifications and unread count for current user
    """
    from flask import g
    user_id = g.user.user_id
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    limit = request.args.get("limit", 20, type=int)

    items, unread_count = notification_service.get_user_notifications(user_id, unread_only=unread_only, limit=limit)
    return jsonify({
        "items": items,
        "unread_count": unread_count,
        "total": len(items)
    }), 200


@api_bp.route("/notifications/<notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read_v1(notification_id):
    """
    Mark specific notification as read
    """
    from flask import g
    user_id = g.user.user_id
    success = notification_service.mark_as_read(user_id, notification_id)
    return jsonify({"success": success}), 200 if success else 404


@api_bp.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read_v1():
    """
    Mark all notifications as read for current user
    """
    from flask import g
    user_id = g.user.user_id
    count = notification_service.mark_all_as_read(user_id)
    return jsonify({"success": True, "updated_count": count}), 200


@api_bp.route("/logs", methods=["POST"])
def receive_frontend_logs():
    """
    Ingest logs from the frontend
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "No JSON payload"}), 400

        level = data.get("level", "info").lower()
        message = data.get("message", "")
        context = data.get("context", {})

        log_message = f"[FRONTEND] {message}"
        
        # Add a flag to context so we know it's from frontend
        context["source"] = "frontend"
        context["client_ip"] = request.remote_addr

        if level == "error":
            logger.error(log_message, extra=context)
        elif level == "warn" or level == "warning":
            logger.warning(log_message, extra=context)
        elif level == "debug":
            logger.debug(log_message, extra=context)
        else:
            logger.info(log_message, extra=context)

        return jsonify({"success": True}), 200
    except Exception as e:
        logger.exception("Failed to ingest frontend logs")
        return jsonify({"success": False, "error": str(e)}), 500


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
        
        # --- Save Prediction to DB via Service & Dispatch Alerts ---
        from flask import g
        user_id = (getattr(g, "user", None) and g.user.user_id) or request.headers.get("X-User-Id") or data.get("user_id")
        report_id = data.get("report_id") or data.get("uploaded_report_id")
        
        if user_id:
            try:
                prediction_id = history_service.save_prediction_result(user_id, results, patient_data, report_id=report_id)
                results["prediction_id"] = prediction_id
                notification_service.dispatch_prediction_notifications(user_id, prediction_id, results)
                logger.info(f"Persisted prediction {prediction_id} for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to persist prediction / dispatch notifications: {e}")
        else:
            logger.warning("Prediction executed without authenticated user_id; record was not persisted to history")
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
            "ai_suggestions":   results.get("ai_suggestions", {}),
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
        
        # ── Save Uploaded Report to Database & Notify ──────────────────────
        from flask import g
        user_id = (getattr(g, "user", None) and g.user.user_id) or request.headers.get("X-User-Id")
        report_id = None
        try:
            report_id = history_service.save_uploaded_report(
                clerk_id=user_id,
                filename=file.filename,
                parsed_data=cleaned,
                method=method,
                file_size=len(pdf_bytes)
            )
            if user_id:
                notification_service.dispatch_pdf_parsed_notification(
                    clerk_id=user_id,
                    report_id=report_id,
                    filename=file.filename,
                    field_count=len(cleaned),
                    method=method
                )
        except Exception as e:
            logger.error(f"Failed to persist uploaded report / notify: {e}")

        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"PDF parsed in {duration_ms:.0f} ms | filename={file.filename} | method={method} | fields_extracted={len(cleaned)}")

        return jsonify({
            "success":    True,
            "extracted":  cleaned,
            "count":      len(cleaned),
            "all_fields": list(cleaned.keys()),
            "method":     method,
            "report_id":  report_id,
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


def _simulate_logic():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            raise ValidationError("request", "No JSON body received.")

        base_inputs = data.get("base_inputs") or data.get("inputs") or {}
        modifications = data.get("modifications") or {}
        base_results = data.get("base_results") or data.get("results")

        if not base_inputs:
            raise ValidationError("base_inputs", "Baseline patient inputs required for simulation.")

        # Clean baseline inputs with standard validator
        validated_base = validate_patient_data(base_inputs)

        sim_result = simulation_service.simulate_risk_reduction(
            base_inputs=validated_base,
            modifications=modifications,
            base_results=base_results
        )

        return jsonify(sim_result), 200

    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": {
                "type": "ValidationError",
                "field": e.field,
                "message": e.message
            }
        }), 400
    except Exception as exc:
        logger.exception("Error in /simulate")
        return jsonify({
            "success": False,
            "error": {
                "type": "SimulationError",
                "message": str(exc)
            }
        }), 500
