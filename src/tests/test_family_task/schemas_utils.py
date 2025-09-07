import jsonschema
import pytest

family_task_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "family_id": {"type": "string", "format": "uuid"},
        "assignee": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
            "required": ["id", "first_name", "last_name"],
            "additionalProperties": False,
        },
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
        "title": {"type": "string"},
        "done": {"type": "boolean"},
    },
    "required": ["id", "family_id", "assignee", "creator", "title", "done"],
    "additionalProperties": False,
}


family_task_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next_page": {"type": ["string", "null"], "format": "uri"},
        "previous_page": {"type": ["string", "null"], "format": "uri"},
        "results": {"type": "array", "items": family_task_response_schema},
    },
    "required": ["count", "next_page", "previous_page", "results"],
    "additionalProperties": False,
}

websocket_task_create_response_schema = {
    "type": "object",
    "properties": {
        "family_id": {"type": "string", "format": "uuid"},
        "event_type": {"const": "user_created_task"},
        "data": family_task_response_schema,
    },
    "required": ["family_id", "event_type", "data"],
    "additionalProperties": False,
}

websocket_task_update_response_schema = {
    "type": "object",
    "properties": {
        "family_id": {"type": "string", "format": "uuid"},
        "event_type": {"const": "user_updated_task"},
        "data": family_task_response_schema,
    },
    "required": ["family_id", "event_type", "data"],
    "additionalProperties": False,
}

websocket_task_update_done_status_response_schema = {
    "type": "object",
    "properties": {
        "family_id": {"type": "string", "format": "uuid"},
        "event_type": {"const": "user_updated_task_done_status"},
        "data": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "done": {"type": "boolean"},
            },
            "required": ["id", "done"],
            "additionalProperties": False,
        },
    },
    "required": ["family_id", "event_type", "data"],
    "additionalProperties": False,
}


def _assert_family_task_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=family_task_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")


def _assert_family_task_list_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=family_task_list_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")


def _assert_websocket_task_create_response_schema(data):
    """Validate that the websocket event matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=websocket_task_create_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"WebSocket event does not match schema: {e}")


def _assert_websocket_task_update_response_schema(data):
    """Validate that the websocket event matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=websocket_task_update_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"WebSocket event does not match schema: {e}")


def _assert_websocket_task_update_done_status_response_schema(data):
    """Validate that the websocket event matches the expected schema."""
    try:
        jsonschema.validate(
            instance=data,
            schema=websocket_task_update_done_status_response_schema,
        )
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"WebSocket event does not match schema: {e}")
