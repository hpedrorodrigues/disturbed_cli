import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.opsgenie.com"


class OpsgenieApi(object):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_on_call_user_email(self, schedule_name: str) -> Optional[str]:
        response = requests.get(
            url=f"{BASE_URL}/v2/schedules/{schedule_name}/on-calls",
            params={"flat": True, "scheduleIdentifierType": "name"},
            headers={"Authorization": f"GenieKey {self.api_key}"},
        )

        if response.status_code == 200:
            recipients = response.json().get("data", {}).get("onCallRecipients", [])
            if not recipients or len(recipients) == 0:
                logger.error(f"Failed to get on-call recipients: {response.text}.")
                return None
            if len(recipients) > 1:
                logger.error(f"More than one recipient returned: {response.text}.")
                return None
            return recipients[0]
        else:
            logger.error(f"Failed to get on-call information [status_code: {response.status_code}]: {response.text}.")
            return None
