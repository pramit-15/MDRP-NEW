class MDRPException(Exception):
    """Base exception class for MDRP application."""
    pass

class ValidationError(MDRPException):
    """Exception raised for invalid input data."""
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed for '{field}': {message}")

class PredictionError(MDRPException):
    """Exception raised when an error occurs during model prediction."""
    pass

class PDFParsingError(MDRPException):
    """Exception raised when there is an issue with parsing or validating a PDF file."""
    pass

class ModelLoadingError(MDRPException):
    """Exception raised when a model fails to load."""
    pass

class ConfigurationError(MDRPException):
    """Exception raised when there is a configuration error."""
    pass
