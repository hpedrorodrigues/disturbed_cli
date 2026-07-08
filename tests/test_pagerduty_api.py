from unittest.mock import Mock, patch

from disturbed.pagerduty import PagerdutyApi
from tests.helpers import fake_response

SCHEDULE_NAME = "sre"
SCHEDULE_ID = "PABC123"
USER_EMAIL = "john.doe@example.com"


def schedules_response(*names_and_ids: tuple[str, str]) -> Mock:
    return fake_response(200, {"schedules": [{"id": id, "name": name} for name, id in names_and_ids]})


def users_response(*emails: str) -> Mock:
    return fake_response(200, {"users": [{"id": f"P{i}", "email": email} for i, email in enumerate(emails)]})


@patch("disturbed.pagerduty.api.requests.get")
def test_returns_on_call_user_email(mock_get):
    mock_get.side_effect = [
        schedules_response((SCHEDULE_NAME, SCHEDULE_ID)),
        users_response(USER_EMAIL),
    ]

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_right
    assert result.value == USER_EMAIL
    assert mock_get.call_args_list[1].kwargs["url"].endswith(f"/schedules/{SCHEDULE_ID}/users")


@patch("disturbed.pagerduty.api.requests.get")
def test_filters_substring_matches_to_exact_name(mock_get):
    mock_get.side_effect = [
        schedules_response(("sre-secondary", "POTHER1"), (SCHEDULE_NAME, SCHEDULE_ID), ("sre-escalation", "POTHER2")),
        users_response(USER_EMAIL),
    ]

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_right
    assert mock_get.call_args_list[1].kwargs["url"].endswith(f"/schedules/{SCHEDULE_ID}/users")


@patch("disturbed.pagerduty.api.requests.get")
def test_fails_when_no_schedule_matches_exact_name(mock_get):
    mock_get.return_value = schedules_response(("sre-secondary", "POTHER1"))

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "No schedule found" in str(result.value)


@patch("disturbed.pagerduty.api.requests.get")
def test_fails_when_multiple_schedules_match_exact_name(mock_get):
    mock_get.return_value = schedules_response((SCHEDULE_NAME, SCHEDULE_ID), (SCHEDULE_NAME, "PDUPLICATE"))

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "More than one schedule" in str(result.value)


@patch("disturbed.pagerduty.api.requests.get")
def test_fails_when_no_user_is_on_call(mock_get):
    mock_get.side_effect = [
        schedules_response((SCHEDULE_NAME, SCHEDULE_ID)),
        users_response(),
    ]

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "Failed to get on-call users" in str(result.value)


@patch("disturbed.pagerduty.api.requests.get")
def test_fails_when_multiple_users_are_on_call(mock_get):
    mock_get.side_effect = [
        schedules_response((SCHEDULE_NAME, SCHEDULE_ID)),
        users_response(USER_EMAIL, "jane.doe@example.com"),
    ]

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "More than one user" in str(result.value)


@patch("disturbed.pagerduty.api.requests.get")
def test_fails_when_schedules_request_fails(mock_get):
    mock_get.return_value = fake_response(401, {"error": {"message": "Unauthorized"}})

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "Failed to find schedule" in str(result.value)


@patch("disturbed.pagerduty.api.requests.get")
def test_fails_when_users_request_fails(mock_get):
    mock_get.side_effect = [
        schedules_response((SCHEDULE_NAME, SCHEDULE_ID)),
        fake_response(500, {"error": {"message": "Internal error"}}),
    ]

    result = PagerdutyApi(api_key="key").get_on_call_user_email(schedule_name=SCHEDULE_NAME)

    assert result.is_left()
    assert "Failed to get on-call information" in str(result.value)


@patch("disturbed.pagerduty.api.requests.get")
def test_caches_schedule_id_between_calls(mock_get):
    mock_get.side_effect = [
        schedules_response((SCHEDULE_NAME, SCHEDULE_ID)),
        users_response(USER_EMAIL),
        users_response(USER_EMAIL),
    ]
    api = PagerdutyApi(api_key="key")

    assert api.get_on_call_user_email(schedule_name=SCHEDULE_NAME).is_right
    assert api.get_on_call_user_email(schedule_name=SCHEDULE_NAME).is_right

    schedule_lookups = [call for call in mock_get.call_args_list if call.kwargs["url"].endswith("/schedules")]
    assert len(schedule_lookups) == 1
