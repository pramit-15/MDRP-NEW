import pytest
import os
from backend.app.config import Config
from backend.app.constants import FIELD_BOUNDS, ALL_LAB_FIELDS

def test_config_loads_defaults():
    # Test that config provides basic default paths
    assert Config.BASE_DIR is not None
    assert "models" in Config.MODELS_DIR
    assert Config.MAX_CONTENT_LENGTH == 8 * 1024 * 1024
    
def test_constants_definitions():
    # Test that essential constants exist and have correct formats
    assert "age" in FIELD_BOUNDS
    assert "bmi" in FIELD_BOUNDS
    assert "glucose" in FIELD_BOUNDS
    
    # Check that FIELD_BOUNDS are tuples (min, max)
    for field, bounds in FIELD_BOUNDS.items():
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        
    assert isinstance(ALL_LAB_FIELDS, list)
    assert len(ALL_LAB_FIELDS) > 0
