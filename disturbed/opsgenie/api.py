import logging

import requests

from disturbed.types import DisturbedApiError, Either

logger = logging.getLogger(__name__)

BASE_URL = "https://api.opsgenie.com"


class OpsgenieApi(object):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_on_call_user_email(self, schedule_name: str) -> Either[DisturbedApiError, str]:
        response = requests.get(
            url=f"{BASE_URL}/v2/schedules/{schedule_name}/on-calls",
            params={"flat": True, "scheduleIdentifierType": "name"},
            headers={"Authorization": f"GenieKey {self.api_key}"},
        )

        if response.status_code == 200:
            recipients = response.json().get("data", {}).get("onCallRecipients", [])
            if not recipients or len(recipients) == 0:
                return Either.left(
                    DisturbedApiError(
                        message=f"Failed to get on-call recipients [schedule_name: {schedule_name}].",
                        status_code=response.status_code,
                        response_body=response.text,
                    )
                )
            if len(recipients) > 1:
                return Either.left(
                    DisturbedApiError(
                        message=f"More than one recipient returned [schedule_name: {schedule_name}].",
                        status_code=response.status_code,
                        response_body=response.text,
                    )
                )
            return Either.right(recipients[0])
        else:
            return Either.left(
                DisturbedApiError(
                    message=f"Failed to get on-call information [schedule_name: {schedule_name}].",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            )
