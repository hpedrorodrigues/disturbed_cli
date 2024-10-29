import os
import sys
from typing import Any, Optional

import yaml
import yamlcore

from disturbed.configuration.types import (
    Config,
    RepeatsOn,
    ScheduleMapping,
    ScheduleOverride,
)
from disturbed.opsgenie.api import logger


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
            config_dict = yaml.load(fd, Loader=yamlcore.CoreLoader)

        mappings: list[ScheduleMapping] = []
        for mapping in config_dict["schedules_mapping"]:
            overrides = None
            if "overrides" in mapping:
                overrides = [
                    ScheduleOverride(
                        user_email=override["user_email"],
                        timezone=override["timezone"],
                        starts_on=override["starts_on"],
                        ends_on=override["ends_on"],
                        repeats_on=RepeatsOn(override["repeats_on"]) if "repeats_on" in override else None,
                        replace_by=override["replace_by"],
                    )
                    for override in mapping["overrides"]
                ]
            mappings.append(
                ScheduleMapping(
                    schedule_name=mapping["schedule_name"],
                    user_group_name=mapping["user_group_name"],
                    overrides=overrides,
                )
            )

        return Config(schedules_mapping=mappings)

    @property
    def schedules_mapping(self) -> list[ScheduleMapping]:
        return self.config.schedules_mapping
