import pytest
from unittest.mock import MagicMock
from backend.utils.validators import validate_patient_data, validate_pdf_file
from backend.utils.exceptions import ValidationError, PDFParsingError

def test_validate_patient_data_valid(sample_patient_data):
    cleaned = validate_patient_data(sample_patient_data)
    assert cleaned["age"] == 45
    assert cleaned["bmi"] == 25.5
    assert cleaned["trestbps"] == 120
    assert cleaned["bloodpressure"] == 80
    assert cleaned["glucose"] == 95

def test_validate_patient_data_invalid_type():
    with pytest.raises(ValidationError) as exc:
        validate_patient_data("not a dict")
    assert exc.value.field == "request"

def test_validate_patient_data_height_weight():
    data = {"height_cm": 175, "weight_kg": 70}
    cleaned = validate_patient_data(data)
    # BMI = 70 / (1.75 ** 2) = 70 / 3.0625 = 22.857... rounded to 22.9
    assert cleaned["bmi"] == 22.9

def test_validate_patient_data_invalid_height():
    data = {"height_cm": "invalid", "weight_kg": 70}
    with pytest.raises(ValidationError) as exc:
        validate_patient_data(data)
    assert exc.value.field == "height_cm"

def test_validate_patient_data_bounds():
    data = {"age": 150} # Bound is usually < 120
    with pytest.raises(ValidationError) as exc:
        validate_patient_data(data)
    assert exc.value.field == "age"

def test_validate_pdf_valid(sample_pdf_file):
    # Mocking a FileStorage-like object
    mock_file = MagicMock()
    mock_file.filename = sample_pdf_file[1]
    
    # Needs a non-zero size
    mock_file.tell.return_value = 1024
    
    # Should not raise
    validate_pdf_file(mock_file)

def test_validate_pdf_invalid_extension():
    mock_file = MagicMock()
    mock_file.filename = "image.png"
    with pytest.raises(PDFParsingError):
        validate_pdf_file(mock_file)

def test_validate_pdf_empty_file():
    mock_file = MagicMock()
    mock_file.filename = "doc.pdf"
    mock_file.tell.return_value = 0
    with pytest.raises(PDFParsingError):
        validate_pdf_file(mock_file)

def test_validate_pdf_no_file():
    with pytest.raises(PDFParsingError):
        validate_pdf_file(None)
