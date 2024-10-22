import logging
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from disturbed.types import DisturbedApiError, DisturbedError, Either

logger = logging.getLogger(__name__)


class SlackApi(object):
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def find_user_group_ids(self, group_names: list[str]) -> Either[DisturbedError, dict[str, str]]:
        try:
            response = self.client.usergroups_list(include_disabled=True)

            group_id_by_name = {
                current["handle"]: current["id"]
                for current in response["usergroups"]
                if current["handle"] in group_names
            }

            missing_group_names = [group_name for group_name in group_names if group_name not in group_id_by_name]
            if missing_group_names:
                return Either.left(
                    DisturbedError(message=f"Could not find user groups in Slack: {missing_group_names}.")
                )

            return Either.right(
                {
                    current["handle"]: current["id"]
                    for current in response["usergroups"]
                    if current["handle"] in group_names
                }
            )
        except SlackApiError as e:
            return Either.left(
                DisturbedApiError(
                    message="Failed to fetch user groups in Slack.",
                    status_code=e.response.status_code,
                    response_body=e.response.data,
                    cause=e,
                )
            )

    def find_user_id_by_email(self, email: str) -> Either[DisturbedError, str]:
        try:
            response = self.client.users_lookupByEmail(email=email)

            user_id = response.get("user", {}).get("id")
            if not user_id:
                return Either.left(DisturbedError(message=f'Could not find user id in Slack for email "{email}".'))

            return Either.right(user_id)
        except SlackApiError as e:
            return Either.left(
                DisturbedApiError(
                    message=f'Failed to fetch user in Slack with email "{email}".',
                    status_code=e.response.status_code,
                    response_body=e.response.data,
                    cause=e,
                )
            )

    def update_user_group_with_user_ids(self, group_id: str, user_ids: list[str]) -> Optional[DisturbedError]:
        try:
            logger.debug(f'Updating Slack user group "{group_id}" with users "{user_ids}".')
            self.client.usergroups_users_update(usergroup=group_id, users=user_ids)
        except SlackApiError as e:
            return DisturbedApiError(
                message=f"Failed to update user group in Slack [group: {group_id}, user_ids: {user_ids}].",
                status_code=e.response.status_code,
                response_body=e.response.data,
                cause=e,
            )

    def update_user_group_with_user_emails(self, group_id: str, user_emails: list[str]) -> Optional[DisturbedError]:
        user_ids = []
        for user_email in user_emails:
            user_id = self.find_user_id_by_email(email=user_email)
            if user_id.is_left():
                return user_id.value
            user_ids.append(user_id.value)

        logger.debug(f'Updating Slack user group "{group_id}" with users "{user_emails}".')
        return self.update_user_group_with_user_ids(group_id=group_id, user_ids=user_ids)
