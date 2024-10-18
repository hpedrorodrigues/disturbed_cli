import logging
import sys

from disturbed.configuration import Configuration, get_env
from disturbed.opsgenie.api import OpsgenieApi
from disturbed.slack.api import SlackApi

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=get_env("DISTURBED_LOG_LEVEL", logging.INFO))

    config = Configuration()
    opsgenie_api = OpsgenieApi(api_key=get_env("DISTURBED_OPSGENIE_API_KEY"))
    slack_api = SlackApi(token=get_env("DISTURBED_SLACK_API_TOKEN"))

    group_id_by_name = slack_api.find_user_group_ids(
        group_names=[mapping.user_group_name for mapping in config.schedules_mapping]
    )
    logger.debug(f"Found groups: [{group_id_by_name}].")

    for schedule in config.schedules_mapping:
        oncall_user_email = opsgenie_api.get_on_call_user_email(
            schedule_name=schedule.schedule_name,
        )
        if not oncall_user_email:
            logger.critical(
                "Invalid on-call user email received! "
                + f"[schedule_name: {schedule.schedule_name}, user_group_name: {schedule.user_group_name}]"
            )
            sys.exit(1)
        user_id = slack_api.find_user_id_by_email(email=oncall_user_email)
        if not user_id:
            logger.critical(
                f'Could not find user "{oncall_user_email}" in Slack! '
                + f"[schedule_name: {schedule.schedule_name}, user_group_name: {schedule.user_group_name}]"
            )
            sys.exit(1)
        logger.info(f'Updating Slack user group "{schedule.user_group_name}" to user "{oncall_user_email}/{user_id}".')
        slack_api.update_user_group(
            group_id=group_id_by_name[schedule.user_group_name],
            user_id=user_id,
        )
    logger.info("All done!")


if __name__ == "__main__":
    main()
