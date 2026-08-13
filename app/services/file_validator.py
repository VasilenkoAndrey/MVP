"""STL file validation utility"""
import stl
import numpy as np


def validate_stl(file_content: bytes) -> dict:
    """Parse STL file and return mesh info"""
    try:
        mesh = stl.Mesh.from_bytes(file_content)
        vectors = mesh.vectors
        min_coords = vectors.min(axis=(0, 1))
        max_coords = vectors.max(axis=(0, 1))
        bbox_size = max_coords - min_coords

        return {
            "valid": True,
            "triangle_count": len(mesh),
            "vertex_count": len(vectors),
            "bounding_box": {
                "min": {"x": float(min_coords[0]), "y": float(min_coords[1]), "z": float(min_coords[2])},
                "max": {"x": float(max_coords[0]), "y": float(max_coords[1]), "z": float(max_coords[2])},
            },
            "dimensions_mm": {
                "x": float(bbox_size[0]),
                "y": float(bbox_size[1]),
                "z": float(bbox_size[2]),
            },
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}
