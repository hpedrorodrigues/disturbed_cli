from typing import Protocol

from disturbed.types.either import Either
from disturbed.types.errors import DisturbedApiError


class OnCallProvider(Protocol):
    def get_on_call_user_email(self, schedule_name: str) -> Either[DisturbedApiError, str]: ...
