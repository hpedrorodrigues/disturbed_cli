import logging
from datetime import datetime, timedelta, timezone

import requests

from disturbed.types import DisturbedApiError, Either

logger = logging.getLogger(__name__)

BASE_URL = "https://api.pagerduty.com"

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class PagerdutyApi(object):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._schedule_id_by_name: dict[str, str] = {}

    def get_on_call_user_email(self, schedule_name: str) -> Either[DisturbedApiError, str]:
        schedule_id = self._find_schedule_id(schedule_name=schedule_name)
        if schedule_id.is_left():
            return schedule_id

        now = datetime.now(timezone.utc)
        response = requests.get(
            url=f"{BASE_URL}/schedules/{schedule_id.value}/users",
            params={
                "since": now.strftime(TIME_FORMAT),
                "until": (now + timedelta(seconds=1)).strftime(TIME_FORMAT),
            },
            headers=self._headers(),
        )

        if response.status_code != 200:
            return Either.left(
                DisturbedApiError(
                    message=f"Failed to get on-call information [schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )

        users = response.json().get("users", [])
        if not users or len(users) == 0:
            return Either.left(
                DisturbedApiError(
                    message=f"Failed to get on-call users [schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )
        if len(users) > 1:
            return Either.left(
                DisturbedApiError(
                    message=f"More than one user returned [schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )

        # The API may return a user reference (no email) instead of a full user object.
        user = users[0]
        if user.get("email"):
            return Either.right(user["email"])
        if user.get("deleted_at"):
            return Either.left(
                DisturbedApiError(
                    message=f'On-call user "{user.get("summary")}" has been deleted in PagerDuty '
                    f"[schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )
        return self._get_user_email(user_id=user["id"], schedule_name=schedule_name)

    def _get_user_email(self, user_id: str, schedule_name: str) -> Either[DisturbedApiError, str]:
        response = requests.get(
            url=f"{BASE_URL}/users/{user_id}",
            headers=self._headers(),
        )

        if response.status_code != 200:
            return Either.left(
                DisturbedApiError(
                    message=f"Failed to get on-call user details [schedule_name: {schedule_name}, user_id: {user_id}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )

        email = response.json().get("user", {}).get("email")
        if not email:
            return Either.left(
                DisturbedApiError(
                    message=f"On-call user has no email [schedule_name: {schedule_name}, user_id: {user_id}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )
        return Either.right(email)

    def _find_schedule_id(self, schedule_name: str) -> Either[DisturbedApiError, str]:
        if schedule_name in self._schedule_id_by_name:
            return Either.right(self._schedule_id_by_name[schedule_name])

        response = requests.get(
            url=f"{BASE_URL}/v3/schedules",
            params={"query": schedule_name, "limit": 100},
            headers=self._headers(),
        )

        if response.status_code != 200:
            return Either.left(
                DisturbedApiError(
                    message=f"Failed to find schedule [schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )

        # The "query" param matches substrings, so an exact-name filter is still needed.
        schedules = response.json().get("schedules", [])
        matches = [schedule for schedule in schedules if schedule.get("summary") == schedule_name]
        if not matches or len(matches) == 0:
            return Either.left(
                DisturbedApiError(
                    message=f"No schedule found with this exact name [schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )
        if len(matches) > 1:
            return Either.left(
                DisturbedApiError(
                    message=f"More than one schedule matches this name [schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )

        schedule_id = matches[0]["id"]
        self._schedule_id_by_name[schedule_name] = schedule_id
        return Either.right(schedule_id)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Token token={self.api_key}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json",
        }
