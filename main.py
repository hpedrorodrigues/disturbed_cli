import logging
import sys

from disturbed.configuration import Configuration, Provider, get_env
from disturbed.handler import ScheduleHandler
from disturbed.opsgenie import OpsgenieApi
from disturbed.pagerduty import PagerdutyApi
from disturbed.slack import SlackApi
from disturbed.types import OnCallProvider

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=get_env("DISTURBED_LOG_LEVEL", logging.INFO),
    )

    config = Configuration()

    used_providers = {mapping.provider for mapping in config.schedules_mapping}
    providers: dict[Provider, OnCallProvider] = {}
    if Provider.OPSGENIE in used_providers:
        providers[Provider.OPSGENIE] = OpsgenieApi(api_key=get_env("DISTURBED_OPSGENIE_API_KEY"))
    if Provider.PAGERDUTY in used_providers:
        providers[Provider.PAGERDUTY] = PagerdutyApi(api_key=get_env("DISTURBED_PAGERDUTY_API_KEY"))

    handler = ScheduleHandler(
        config=config,
        providers=providers,
        slack_api=SlackApi(token=get_env("DISTURBED_SLACK_API_TOKEN")),
    )
    error = handler.process()
    if error:
        logger.critical(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
