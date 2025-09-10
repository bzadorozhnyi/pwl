import jsonschema
import pytest

shopping_list_item_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "name": {"type": "string", "minLength": 1},
        "shopping_list_id": {"type": "string", "format": "uuid"},
        "purchased": {"type": "boolean"},
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
    "required": ["shopping_list_id", "name", "purchased", "id", "creator"],
    "additionalProperties": False,
}

shopping_list_item_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next_page": {"type": ["string", "null"], "format": "uri"},
        "previous_page": {"type": ["string", "null"], "format": "uri"},
        "results": {"type": "array", "items": shopping_list_item_response_schema},
    },
    "required": ["count", "next_page", "previous_page", "results"],
    "additionalProperties": False,
}

websocket_shopping_list_item_create_response_schema = {
    "type": "object",
    "properties": {
        "family_id": {"type": "string", "format": "uuid"},
        "event_type": {"const": "user_created_shopping_list_item"},
        "data": shopping_list_item_response_schema,
    },
    "required": ["family_id", "event_type", "data"],
    "additionalProperties": False,
}

websocket_shopping_list_item_update_purchased_status_response_schema = {
    "type": "object",
    "properties": {
        "family_id": {"type": "string", "format": "uuid"},
        "event_type": {"const": "user_updated_shopping_list_item_purchased_status"},
        "data": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "purchased": {"type": "boolean"},
            },
            "required": ["id", "purchased"],
            "additionalProperties": False,
        },
    },
    "required": ["family_id", "event_type", "data"],
    "additionalProperties": False,
}


def _assert_shopping_list_item_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=shopping_list_item_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")


def _assert_shopping_list_item_list_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(
            instance=data, schema=shopping_list_item_list_response_schema
        )
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")


def _assert_websocket_shopping_list_item_create_response_schema(data):
    """Validate that the WebSocket response for shopping list item creation matches the expected schema."""
    try:
        jsonschema.validate(
            instance=data, schema=websocket_shopping_list_item_create_response_schema
        )
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"WebSocket response does not match schema: {e}")


def _assert_websocket_update_purchased_status_response_schema(data):
    """Validate that the WebSocket response for shopping list item purchased status update matches the expected schema."""
    try:
        jsonschema.validate(
            instance=data,
            schema=websocket_shopping_list_item_update_purchased_status_response_schema,
        )
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"WebSocket response does not match schema: {e}")
