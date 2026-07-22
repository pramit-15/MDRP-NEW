import os
from backend.app.constants import FIELD_BOUNDS, ALL_LAB_FIELDS
from backend.utils.exceptions import ValidationError, PDFParsingError

def validate_patient_data(data: dict) -> dict:
    """
    Validates patient data and returns a cleaned dictionary with proper types.
    Raises ValidationError if validation fails.
    """
    if not isinstance(data, dict):
        raise ValidationError("request", "Data must be a JSON object.")
        
    cleaned = {}
    
    # Process height, weight, bmi
    height_cm = data.get("height_cm")
    weight_kg = data.get("weight_kg")
    
    height_val, weight_val = None, None
    if height_cm is not None and height_cm != "":
        try:
            height_val = float(height_cm)
            _check_bounds("height_cm", height_val)
        except ValueError:
            raise ValidationError("height_cm", "Height must be a numeric value.")
            
    if weight_kg is not None and weight_kg != "":
        try:
            weight_val = float(weight_kg)
            _check_bounds("weight_kg", weight_val)
        except ValueError:
            raise ValidationError("weight_kg", "Weight must be a numeric value.")
            
    if height_val is not None and weight_val is not None and height_val > 0:
        bmi = round(weight_val / ((height_val / 100) ** 2), 1)
        cleaned["bmi"] = bmi
    else:
        bmi_raw = data.get("bmi")
        if bmi_raw is not None and bmi_raw != "":
            try:
                bmi = float(bmi_raw)
                _check_bounds("bmi", bmi)
                cleaned["bmi"] = bmi
            except ValueError:
                raise ValidationError("bmi", "BMI must be a numeric value.")

    # Base fields that the API always expects (age, sex, preg)
    for field in ["age", "sex", "preg"]:
        raw = data.get(field)
        if raw is not None and raw != "":
            try:
                val = float(raw)
                if field in ["sex", "preg"]:
                    val = int(val)
                _check_bounds(field, val)
                cleaned[field] = val
            except ValueError:
                raise ValidationError(field, f"{field.capitalize()} must be a numeric value.")

    # Blood pressure handling
    sys = data.get("systolic_bp")
    dia = data.get("diastolic_bp")
    
    if sys is not None and sys != "":
        try:
            sys_val = float(sys)
            _check_bounds("systolic_bp", sys_val)
            cleaned["trestbps"] = sys_val
            cleaned["systolic_bp"] = sys_val
        except ValueError:
            raise ValidationError("systolic_bp", "Systolic BP must be a numeric value.")
            
    if dia is not None and dia != "":
        try:
            dia_val = float(dia)
            _check_bounds("diastolic_bp", dia_val)
            cleaned["bloodpressure"] = dia_val
            cleaned["bp"] = dia_val
            cleaned["diastolic_bp"] = dia_val
        except ValueError:
            raise ValidationError("diastolic_bp", "Diastolic BP must be a numeric value.")

    # Other lab fields
    for field in ALL_LAB_FIELDS:
        raw = data.get(field)
        if raw is None or raw == "":
            continue
            
        try:
            val = float(raw)
        except ValueError:
            raise ValidationError(field, f"{field} must be a numeric value.")
            
        _check_bounds(field, val)
        cleaned[field] = val
        
    return cleaned

def _check_bounds(field: str, value: float):
    if field in FIELD_BOUNDS:
        lo, hi = FIELD_BOUNDS[field]
        if not (lo <= value <= hi):
            raise ValidationError(field, f"{field} must be between {lo} and {hi}.")

def validate_pdf_file(file):
    if not file:
        raise PDFParsingError("No file provided.")
        
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise PDFParsingError("Only PDF files are accepted.")
        
    # Check if empty without destroying file pointer
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size == 0:
        raise PDFParsingError("Uploaded file is empty.")
    
    # The max content length is usually handled by Flask, but just to be safe
    # we could check here too, but size limit is enforced by app config.
