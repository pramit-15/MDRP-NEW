import json
import numpy as np
from datetime import datetime

class NumpyEncoder(json.JSONEncoder):
    """ Custom encoder for NumPy data types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(NumpyEncoder, self).default(obj)

def make_json_safe(obj):
    """
    Converts NumPy and Pandas objects to native Python structures
    so they can be safely serialized to JSON and stored in PostgreSQL JSONB.
    Optimized by using json.loads(json.dumps()) with custom NumpyEncoder.
    """
    if hasattr(obj, 'to_dict'):
        obj = obj.to_dict()
    return json.loads(json.dumps(obj, cls=NumpyEncoder))
