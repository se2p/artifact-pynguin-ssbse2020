"""
This module provides common error definitions and routines for :py:mod:`pypara`.
"""

__all__ = ["ProgrammingError"]

from typing import Optional


class ProgrammingError(Exception):
    """
    Provides a programming error exception.

    The rationale for this exception is to raise them whenever we rely on meta-programming and the programmer has
    introduced a statement which breaks the coherence of the domain logic.
    """

    @classmethod
    def passert(cls, condition: bool, message: Optional[str]) -> None:
        """
        Raises a :py:class:`ProgrammingError` if the condition is ``False``.

        :param condition: Indicates if the expectation is fulfilled.
        :param message: Message of the error to be raised in case that the condition is not met.
        :raises ProgrammingError: In case that the condition is ``False``.
        """
        if not condition:
            raise cls(message or "Broken coherence. Check your code against domain logic to fix it.")
