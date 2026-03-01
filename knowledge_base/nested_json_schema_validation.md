# Nested JSON Schema Validation Using Recursive Traversal

Summary:
Validates nested dictionary structures recursively.
Ensures required fields exist and types match expected schema.
Handles deep nested objects and type mismatches.

---

## Problem

When validating nested configuration objects such as:

{
    "server": {
        "host": "localhost",
        "port": 8000
    }
}

Simple shallow validation fails to catch missing nested fields or wrong types.

---

## Approach

Use recursive traversal of both schema and data.
At each level:
- Ensure key exists.
- If nested dictionary, recurse.
- If primitive type, validate type.

---

## Example Schema

schema = {
    "server": {
        "host": str,
        "port": int
    }
}

---

## Example Implementation

def validate_schema(data, schema):
    for key, expected in schema.items():
        if key not in data:
            raise ValueError(f"Missing required nested field: {key}")

        if isinstance(expected, dict):
            if not isinstance(data[key], dict):
                raise TypeError(f"Field {key} must be a dict")
            validate_schema(data[key], expected)
        else:
            if not isinstance(data[key], expected):
                raise TypeError(
                    f"Field {key} must be {expected.__name__}"
                )

---

## Notes

- Extend to handle optional fields.
- Extend to handle lists.
- Can integrate into config loading pipeline.