import logging
import sys

from disturbed.configuration import Configuration, get_env
from disturbed.handler import ScheduleHandler
from disturbed.opsgenie import OpsgenieApi
from disturbed.slack import SlackApi

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=get_env("DISTURBED_LOG_LEVEL", logging.INFO),
    )

    handler = ScheduleHandler(
        config=Configuration(),
        opsgenie_api=OpsgenieApi(api_key=get_env("DISTURBED_OPSGENIE_API_KEY")),
        slack_api=SlackApi(token=get_env("DISTURBED_SLACK_API_TOKEN")),
    )
    error = handler.process()
    if error:
        logger.critical(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
