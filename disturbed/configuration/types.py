from dataclasses import dataclass
from typing import Optional

ALL_DAYS = "all_days"
WEEKDAYS = "weekdays"
WEEKENDS = "weekends"


@dataclass
class ScheduleOverride:
    when_user: str
    from_time: str
    to_time: str
    with_timezone: str
    on: str
    replace_by: list[str]


@dataclass
class ScheduleMapping:
    """
    Represents a schedule configuration linking an OpsGenie schedule to a Slack user group.

    Attributes:
        schedule_name (str): The name of the schedule in OpsGenie. This is used to query
                             OpsGenie for the current on-call user.

        user_group_name (str): The name of the Slack user group to be updated. This group will be updated
                               with the current on-call user.
    """

    schedule_name: str
    user_group_name: str
    overrides: Optional[list[ScheduleOverride]]


@dataclass
class Config:
    schedules_mapping: list[ScheduleMapping]
