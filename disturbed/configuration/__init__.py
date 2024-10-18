import os
import sys
from dataclasses import dataclass
from typing import Any, Optional

import yaml

from disturbed.opsgenie.api import logger


@dataclass
class ScheduleMapping:
    """
    Represents a schedule configuration linking an Opsgenie schedule to a Slack user group.

    Attributes:
        schedule_name (str): The name of the schedule in Opsgenie. This is used to query
                             Opsgenie for the current on-call user.

        user_group_name (str): The name of the Slack user group to be updated. This group will be updated
                               with the current on-call user.
    """

    schedule_name: str
    user_group_name: str


@dataclass
class Config:
    schedules_mapping: list[ScheduleMapping]


def get_env(var_name: str, default_value: Optional[Any] = None) -> Any:
    value = os.getenv(var_name)
    if value is None:
        if default_value is None:
            logger.error(f'Environment variable "{var_name}" is not set.')
            sys.exit(1)
        else:
            return default_value
    return value


class Configuration(object):
    def __init__(self, path: str = get_env("DISTURBED_CONFIG_FILE", "config.yaml")):
        self.path = path
        self.config = self._load()

    def _load(self) -> Config:
        with open(self.path, "r") as fd:
            config_dict = yaml.safe_load(fd)
        return Config(schedules_mapping=[ScheduleMapping(**schedule) for schedule in config_dict["schedules_mapping"]])

    @property
    def schedules_mapping(self) -> list[ScheduleMapping]:
        return self.config.schedules_mapping
