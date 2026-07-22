import pytest
from backend.utils.exceptions import MDRPException, ValidationError, PDFParsingError, PredictionError, ModelLoadingError

def test_base_exception():
    exc = MDRPException("Base error message")
    assert str(exc) == "Base error message"

def test_validation_error():
    exc = ValidationError("age", "Age must be positive")
    assert exc.field == "age"
    assert exc.message == "Age must be positive"
    assert str(exc) == "Validation failed for 'age': Age must be positive"

def test_pdf_parsing_error():
    exc = PDFParsingError("Could not extract text")
    assert str(exc) == "Could not extract text"

def test_prediction_error():
    exc = PredictionError("Model prediction failed")
    assert str(exc) == "Model prediction failed"

def test_model_load_error():
    exc = ModelLoadingError("Heart model missing")
    assert str(exc) == "Heart model missing"
