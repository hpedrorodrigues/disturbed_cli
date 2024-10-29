import logging
from typing import Optional

from disturbed.configuration import Configuration, ScheduleMapping, ScheduleOverride
from disturbed.configuration.types import RepeatsOn
from disturbed.handler.time import is_time_between, is_weekday
from disturbed.opsgenie.api import OpsgenieApi
from disturbed.slack.api import SlackApi
from disturbed.types import Either
from disturbed.types.errors import DisturbedError

logger = logging.getLogger(__name__)


class ScheduleHandler(object):
    def __init__(self, config: Configuration, opsgenie_api: OpsgenieApi, slack_api: SlackApi):
        self.config = config
        self.opsgenie_api = opsgenie_api
        self.slack_api = slack_api

    def process(self) -> Optional[DisturbedError]:
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
                continue_processing = True
                for override in schedule.overrides:
                    override_applied = self._apply_override(
                        oncall_user_email=oncall_user_email.value,
                        schedule=schedule,
                        override=override,
                        group_id_by_name=group_id_by_name.value,
                    )
                    if override_applied.is_left():
                        return override_applied.value
                    if override_applied.value:
                        continue_processing = False
                        break
                if not continue_processing:
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

    def _apply_override(
        self,
        oncall_user_email: str,
        schedule: ScheduleMapping,
        override: ScheduleOverride,
        group_id_by_name: dict[str, str],
    ) -> Either[DisturbedError, bool]:
        if oncall_user_email != override.user_email:
            return Either.right(False)

        is_on_repeat = (
            not override.repeats_on
            or override.repeats_on == RepeatsOn.ALL_DAYS
            or (override.repeats_on == RepeatsOn.WEEKDAYS and is_weekday(override.timezone))
            or (override.repeats_on == RepeatsOn.WEEKENDS and not is_weekday(override.timezone))
        )
        if not is_on_repeat:
            return Either.right(False)

        is_time_within_range = is_time_between(
            timezone=override.timezone,
            from_time=override.starts_on,
            to_time=override.ends_on,
        )
        if is_time_within_range.is_left():
            return is_time_within_range
        if not is_time_within_range.value:
            return Either.right(False)

        logger.info(
            f'Updating Slack user group "{schedule.user_group_name}" to users "{override.replace_by}" due to override.'
        )
        error = self.slack_api.update_user_group_with_user_emails(
            group_id=group_id_by_name[schedule.user_group_name],
            user_emails=override.replace_by,
        )
        return Either.left(error) if error else Either.right(True)
