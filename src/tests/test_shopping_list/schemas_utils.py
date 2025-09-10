import jsonschema
import pytest

shopping_list_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "family_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string", "minLength": 1},
        "creator": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
            "required": ["id", "first_name", "last_name"],
            "additionalProperties": False,
        },
    },
    "required": ["id", "family_id", "name", "creator"],
    "additionalProperties": False,
}

# List of shopping lists schema
shopping_list_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next_page": {"type": ["string", "null"], "format": "uri"},
        "previous_page": {"type": ["string", "null"], "format": "uri"},
        "results": {"type": "array", "items": shopping_list_response_schema},
    },
    "required": ["count", "next_page", "previous_page", "results"],
    "additionalProperties": False,
}

websocket_shopping_list_delete_event_response_schema = {
    "type": "object",
    "properties": {
        "family_id": {"type": "string", "format": "uuid"},
        "event_type": {"const": "user_deleted_shopping_list"},
        "data": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    "required": ["family_id", "event_type", "data"],
    "additionalProperties": False,
}


def _assert_shopping_list_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=shopping_list_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")


def _assert_shopping_list_list_response_schema(data):
    """Validate that the list response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=shopping_list_list_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"List response does not match schema: {e}")


def _assert_websocket_shopping_list_delete_event_response_schema(data):
    """Validate that the list response matches the expected schema."""
    try:
        jsonschema.validate(
            instance=data, schema=websocket_shopping_list_delete_event_response_schema
        )
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"List response does not match schema: {e}")
