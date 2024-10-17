import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackApi(object):
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def update_user_group(self, group_name: str, user_id: str):
        try:
            response = self.client.usergroups_users_update(usergroup=group_name, users=user_id)

            if response.status_code != 200:
                logger.error(f"Failed to update user group [group: {group_name}, user_id: {user_id}].")
        except SlackApiError:
            logger.error(
                f"Failed to update user group [group: {group_name}, user_id: {user_id}].",
                exc_info=True,
            )
