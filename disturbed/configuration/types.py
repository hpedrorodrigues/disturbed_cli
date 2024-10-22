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
    schedule_name: str
    user_group_name: str
    overrides: Optional[list[ScheduleOverride]]


@dataclass
class Config:
    schedules_mapping: list[ScheduleMapping]
