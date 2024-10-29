from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar, Union, cast

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

    def map(self, f: Callable[[R], A]) -> "Either[L, A]":
        """
        Apply a function to the Right value, leaving Left values unchanged.
        """
        if self.is_right:
            return Either.right(f(cast(R, self.value)))
        return Either.left(cast(L, self.value))

    def map_left(self, f: Callable[[L], A]) -> "Either[A, R]":
        """
        Apply a function to the Left value, leaving Right values unchanged.
        """
        if self.is_left():
            return Either.left(f(cast(L, self.value)))
        return Either.right(cast(R, self.value))

    def get_or_else(self, default: R) -> R:
        """
        Get the Right value or a default if this is a Left.
        """
        if self.is_right:
            return cast(R, self.value)
        return default

    def get_or_else_get(self, f: Callable[[], R]) -> R:
        """
        Get the Right value or compute a default if this is a Left.
        """
        if self.is_right:
            return cast(R, self.value)
        return f()

    def or_else(self, other: "Either[L, R]") -> "Either[L, R]":
        """
        Return this Either if it's a Right, otherwise return the other Either.
        """
        if self.is_right:
            return self
        return other

    def or_else_get(self, f: Callable[[], "Either[L, R]"]) -> "Either[L, R]":
        """
        Return this Either if it's a Right, otherwise compute and return another Either.
        """
        if self.is_right:
            return self
        return f()

    def contains(self, value: R) -> bool:
        """
        Check if this Either is a Right and contains the given value.
        """
        if not self.is_right:
            return False
        return cast(R, self.value) == value

    def exists(self, predicate: Callable[[R], bool]) -> bool:
        """
        Check if this Either is a Right and its value satisfies the predicate.
        """
        if not self.is_right:
            return False
        return predicate(cast(R, self.value))

    def filter_or_else(self, predicate: Callable[[R], bool], zero: L) -> "Either[L, R]":
        """
        Convert this Either to a Left if it's a Right and fails the predicate.
        """
        if self.is_right:
            right_value = cast(R, self.value)
            if not predicate(right_value):
                return Either.left(zero)
            return self
        return self

    def to_optional(self) -> Optional[R]:
        """
        Convert this Either to an Optional, discarding the Left value.
        """
        if self.is_right:
            return cast(R, self.value)
        return None
