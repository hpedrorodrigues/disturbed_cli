from unittest.mock import Mock, patch

from disturbed.opsgenie import OpsgenieApi
from tests.helpers import fake_response

SCHEDULE_NAME = "sre"
USER_EMAIL = "john.doe@example.com"


def on_calls_response(*emails: str) -> Mock:
    return fake_response(200, {"data": {"onCallRecipients": list(emails)}})


@patch("disturbed.opsgenie.api.requests.get")
def test_returns_on_call_user_email(mock_get):
    mock_get.return_value = on_calls_response(USER_EMAIL)

    result = OpsgenieApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_right
    assert result.value == USER_EMAIL
    assert mock_get.call_args.kwargs["url"].endswith(f"/v2/schedules/{SCHEDULE_NAME}/on-calls")
    assert mock_get.call_args.kwargs["params"]["scheduleIdentifierType"] == "name"


@patch("disturbed.opsgenie.api.requests.get")
def test_fails_when_no_recipient_is_on_call(mock_get):
    mock_get.return_value = on_calls_response()

    result = OpsgenieApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "Failed to get on-call recipients" in str(result.value)


@patch("disturbed.opsgenie.api.requests.get")
def test_fails_when_multiple_recipients_are_on_call(mock_get):
    mock_get.return_value = on_calls_response(USER_EMAIL, "jane.doe@example.com")

    result = OpsgenieApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "More than one recipient returned" in str(result.value)


@patch("disturbed.opsgenie.api.requests.get")
def test_fails_when_request_fails(mock_get):
    mock_get.return_value = fake_response(401, {"message": "Could not authenticate."})

    result = OpsgenieApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "Failed to get on-call information" in str(result.value)
