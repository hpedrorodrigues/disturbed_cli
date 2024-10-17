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

    def find_user_ids(self, user_names: list[str]) -> Optional[dict[str, str]]:
        try:
            # TODO: this approach doesn't work for big workspaces and need to be replaced
            response = self.client.users_list()
            return {
                current["profile"]["display_name"]: current["id"]
                for current in response["members"]
                if current["profile"]["display_name"] in user_names
            }
        except SlackApiError:
            logger.error(f"Failed to fetch users [users: {user_names}].", exc_info=True)

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
