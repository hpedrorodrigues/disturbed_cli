import logging

from disturbed.configuration import Configuration, get_env
from disturbed.opsgenie.api import OpsgenieApi
from disturbed.slack.api import SlackApi

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    config = Configuration()
    opsgenieApi = OpsgenieApi(api_key=get_env("OPSGENIE_API_KEY"))
    slackApi = SlackApi(token=get_env("SLACK_API_TOKEN"))

    for schedule_mapping in config.schedules_mapping:
        oncall_user_email = opsgenieApi.get_on_call_user_email(schedule_name=schedule_mapping.schedule_name)
        user_mapping = config.find_user_by_email(email=oncall_user_email)
        if not user_mapping:
            logger.warning(
                f"User {oncall_user_email} is not mapped! [schedule_name: {schedule_mapping.schedule_name}, user_group_name: {schedule_mapping.user_group_name}]"
            )
            continue
        slackApi.update_user_group(group_name=schedule_mapping.user_group_name, user_id=user_mapping.alias)
    logger.info("All done!")


if __name__ == "__main__":
    main()
