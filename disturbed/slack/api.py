import logging
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackApi(object):
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def find_user_group_ids(self, group_names: list[str]) -> Optional[dict[str, str]]:
        try:
            response = self.client.usergroups_list()
            return {
                current["handle"]: current["id"]
                for current in response["usergroups"]
                if current["handle"] in group_names
            }
        except SlackApiError:
            logger.error(f"Failed to fetch user groups [groups: {group_names}].", exc_info=True)

    def find_user_id_by_email(self, email: str) -> Optional[str]:
        try:
            response = self.client.users_lookupByEmail(email=email)
            return response["user"]["id"]
        except SlackApiError:
            logger.error(f"Failed to fetch user [email={email}].", exc_info=True)

    def update_user_group(self, group_id: str, user_id: str):
        try:
            response = self.client.usergroups_users_update(usergroup=group_id, users=user_id)

            if response.status_code != 200:
                logger.error(f"Failed to update user group [group: {group_id}, user_id: {user_id}].")
        except SlackApiError:
            logger.error(
                f"Failed to update user group [group: {group_id}, user_id: {user_id}].",
                exc_info=True,
            )
