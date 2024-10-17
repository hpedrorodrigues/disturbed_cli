import os
import sys
from dataclasses import dataclass
from typing import Optional

import yaml

from disturbed.opsgenie.api import logger


@dataclass
class UserMapping:
    """
    Represents a mapping between a Slack user and an Opsgenie user.

    Attributes:
        handle (str): The Slack user identifier. This is used to mention or identify the user in Slack.

        email (str): The Opsgenie user's email address. This is used to identify
                     the user in Opsgenie and is typically the user's work email.
    """

    handle: str
    email: str


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
    users_mapping: list[UserMapping]
    schedules_mapping: list[ScheduleMapping]


class Configuration(object):
    def __init__(self, path: str = "config.yaml"):
        self.path = path
        self.config = self._load()

    def _load(self) -> Config:
        with open(self.path, "r") as fd:
            config_dict = yaml.safe_load(fd)
        return Config(
            users_mapping=[UserMapping(**user) for user in config_dict["users_mapping"]],
            schedules_mapping=[ScheduleMapping(**schedule) for schedule in config_dict["schedules_mapping"]],
        )

    def find_user_by_email(self, email: str) -> Optional[UserMapping]:
        return next((mapping for mapping in self.config.users_mapping if mapping.email == email), None)

    @property
    def users_mapping(self) -> list[UserMapping]:
        return self.config.users_mapping

    @property
    def schedules_mapping(self) -> list[ScheduleMapping]:
        return self.config.schedules_mapping


def get_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        logger.error(f'Environment variable "{var_name}" is not set.')
        sys.exit(1)
    return value
