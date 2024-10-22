from dataclasses import dataclass
from typing import Generic, TypeVar, Union

L = TypeVar("L")  # Left type
R = TypeVar("R")  # Right type
A = TypeVar("A")  # New type for map/bind operations


@dataclass
class Either(Generic[L, R]):
    """
    A class representing a value that can be either of two types: Left or Right.
    Typically used to represent a computation that might fail, where:
    - Left represents failure/error
    - Right represents success/value
    """

    value: Union[L, R]
    is_right: bool

    @staticmethod
    def right(value: R) -> "Either[L, R]":
        return Either(value, True)

    @staticmethod
    def left(value: L) -> "Either[L, R]":
        return Either(value, False)

    def is_left(self) -> bool:
        return not self.is_right
