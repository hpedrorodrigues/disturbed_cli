import logging

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
    user_id_by_name = slack_api.find_user_ids(
        user_names=[mapping.handle for mapping in config.users_mapping],
    )
    logger.debug(f"Found users: [{user_id_by_name}].")

    for schedule in config.schedules_mapping:
        oncall_user_email = opsgenie_api.get_on_call_user_email(
            schedule_name=schedule.schedule_name,
        )
        if not oncall_user_email:
            logger.warning(
                "Invalid on-call user email received! Ignoring... "
                + f"[schedule_name: {schedule.schedule_name}, user_group_name: {schedule.user_group_name}]"
            )
            continue
        user = config.find_user_by_email(
            email=oncall_user_email,
        )
        if not user:
            logger.warning(
                f"User {oncall_user_email} is not mapped! Ignoring... "
                + f"[schedule_name: {schedule.schedule_name}, user_group_name: {schedule.user_group_name}]"
            )
            continue
        logger.info(f'Updating user group "{schedule.user_group_name}" to user "{user.handle}".')
        slack_api.update_user_group(
            group_id=group_id_by_name[schedule.user_group_name],
            user_id=user_id_by_name[user.handle],
        )
    logger.info("All done!")


if __name__ == "__main__":
    main()
