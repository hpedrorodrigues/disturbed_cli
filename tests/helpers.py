import json
from unittest.mock import Mock


def fake_response(status_code: int, body: dict) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.json.return_value = body
    response.text = json.dumps(body)
    return response
