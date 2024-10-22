from datetime import datetime, time
from typing import Optional
from zoneinfo import ZoneInfo

from disturbed.types import DisturbedError, Either


def is_time_between(timezone: str, from_time: str, to_time: str) -> Either[DisturbedError, bool]:
    return TimeChecker(timezone).is_time_between(from_time, to_time)


def is_weekday(timezone: str) -> bool:
    return TimeChecker(timezone).is_weekday()


class TimeChecker:
    def __init__(self, timezone: str):
        self.timezone = ZoneInfo(timezone)

    def is_weekday(self) -> bool:
        current_date_time = datetime.now(self.timezone)
        return current_date_time.weekday() < 5  # Saturday=5, Sunday=6

    def is_time_between(self, from_time: str, to_time: str) -> Either[DisturbedError, bool]:
        time_from = self._parse_time(from_time)
        if not time_from:
            return Either.left(DisturbedError(f'Invalid time format for "{from_time}". Use HH:MM:SS.'))

        time_to = self._parse_time(to_time)
        if not time_to:
            return Either.left(DisturbedError(f'Invalid time format for "{to_time}". Use HH:MM:SS.'))

        current_time = datetime.now(self.timezone).time()
        if time_from <= time_to:
            return Either.right(time_from <= current_time <= time_to)
        else:
            return Either.right(current_time >= time_from or current_time <= time_to)

    def _parse_time(self, time_str: str) -> Optional[time]:
        try:
            return datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            return None
