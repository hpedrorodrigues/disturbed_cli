import logging
from typing import Optional

from disturbed.configuration import Configuration
from disturbed.configuration.types import ALL_DAYS, WEEKDAYS, WEEKENDS
from disturbed.handler.time import is_time_between, is_weekday
from disturbed.opsgenie.api import OpsgenieApi
from disturbed.slack.api import SlackApi
from disturbed.types.errors import DisturbedError

logger = logging.getLogger(__name__)


class ScheduleHandler(object):
    def __init__(self, config: Configuration, opsgenie_api: OpsgenieApi, slack_api: SlackApi):
        self.config = config
        self.opsgenie_api = opsgenie_api
        self.slack_api = slack_api

    def handle_schedules(self) -> Optional[DisturbedError]:
        group_id_by_name = self.slack_api.find_user_group_ids(
            group_names=[mapping.user_group_name for mapping in self.config.schedules_mapping]
        )
        if group_id_by_name.is_left():
            return group_id_by_name.value

        for schedule in self.config.schedules_mapping:
            oncall_user_email = self.opsgenie_api.get_on_call_user_email(schedule_name=schedule.schedule_name)
            if oncall_user_email.is_left():
                return oncall_user_email.value

            if schedule.overrides:
                schedule_processed = False
                for override in schedule.overrides:
                    is_on_valid_day = (
                        override.on == ALL_DAYS
                        or (override.on == WEEKDAYS and is_weekday(override.with_timezone))
                        or (override.on == WEEKENDS and not is_weekday(override.with_timezone))
                    )
                    if not is_on_valid_day:
                        continue

                    is_time_within_range = is_time_between(override.with_timezone, override.from_time, override.to_time)
                    if is_time_within_range.is_left():
                        return is_time_within_range.value

                    if not is_time_within_range.value:
                        continue

                    logger.info(
                        f'Updating Slack user group "{schedule.user_group_name}" to users "{override.replace_by}" due to override.'
                    )
                    error = self.slack_api.update_user_group_with_user_emails(
                        group_id=group_id_by_name.value[schedule.user_group_name],
                        user_emails=override.replace_by,
                    )
                    if error:
                        return error
                    else:
                        schedule_processed = True
                if schedule_processed:
                    continue

            logger.info(
                f'Updating Slack user group "{schedule.user_group_name}" to users "[\'{oncall_user_email.value}\']".'
            )
            error = self.slack_api.update_user_group_with_user_emails(
                group_id=group_id_by_name.value[schedule.user_group_name],
                user_emails=[oncall_user_email.value],
            )
            if error:
                return error
        logger.info("All done!")
