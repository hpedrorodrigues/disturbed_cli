import logging

from disturbed.configuration import Configuration, get_env
from disturbed.opsgenie.api import OpsgenieApi
from disturbed.slack.api import SlackApi

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    config = Configuration()
    opsgenie_api = OpsgenieApi(api_key=get_env("OPSGENIE_API_KEY"))
    slack_api = SlackApi(token=get_env("SLACK_API_TOKEN"))

    group_id_by_name = slack_api.find_user_group_ids(
        group_names=[mapping.user_group_name for mapping in config.schedules_mapping]
    )
    user_id_by_name = slack_api.find_user_ids(
        user_names=[mapping.handle for mapping in config.users_mapping],
    )

    for schedule_mapping in config.schedules_mapping:
        oncall_user_email = opsgenie_api.get_on_call_user_email(
            schedule_name=schedule_mapping.schedule_name,
        )
        if not oncall_user_email:
            logger.warning(
                f"Invalid on-call user email received! Ignoring... [schedule_name: {schedule_mapping.schedule_name}, user_group_name: {schedule_mapping.user_group_name}]"
            )
            continue
        user_mapping = config.find_user_by_email(
            email=oncall_user_email,
        )
        if not user_mapping:
            logger.warning(
                f"User {oncall_user_email} is not mapped! Ignoring... [schedule_name: {schedule_mapping.schedule_name}, user_group_name: {schedule_mapping.user_group_name}]"
            )
            continue
        slack_api.update_user_group(
            group_id=group_id_by_name[schedule_mapping.user_group_name],
            user_id=user_id_by_name[user_mapping.handle],
        )
    logger.info("All done!")


if __name__ == "__main__":
    main()
