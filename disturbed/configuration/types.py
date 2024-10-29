from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RepeatsOn(Enum):
    ALL_DAYS = "all_days"
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"


@dataclass
class ScheduleOverride:
    user_email: str
    timezone: str
    starts_on: str
    ends_on: str
    repeats_on: Optional[RepeatsOn]
    replace_by: list[str]


@dataclass
class ScheduleMapping:
    schedule_name: str
    user_group_name: str
    overrides: Optional[list[ScheduleOverride]]


@dataclass
class Config:
    schedules_mapping: list[ScheduleMapping]
