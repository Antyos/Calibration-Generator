from typing import Union
from euclid import Vector2, Vector3

def vec_to_dict(vec: Union[Vector2, Vector3]) -> dict:
    """Convert a Euclid Vector2 or Vector3 to a dict."""
    if isinstance(vec, Vector2):
        return {'x': vec.x, 'y': vec.y}
    elif isinstance(vec, Vector3):
        return {"x": vec.x, 'y': vec.y, 'z': vec.z}
    else:
        raise TypeError
