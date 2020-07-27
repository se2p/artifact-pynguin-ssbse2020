"""
This module provides definitions and functionality related to foreign-exchange conversions.
"""

__all__ = ["FXRate", "FXRateLookupError", "FXRateService"]

from abc import ABCMeta, abstractmethod
from decimal import Decimal
from typing import Iterable, NamedTuple, Optional, Tuple

from .commons.numbers import ONE, ZERO
from .commons.zeitgeist import Date
from .currencies import Currency


class FXRateLookupError(LookupError):
    """
    Provides an exception indicating that the foreign exchange rate is not found.
    """

    def __init__(self, ccy1: Currency, ccy2: Currency, asof: Date) -> None:
        """
        Initializes the foreign exchange rate lookup error.
        """
        ## Keep the slots:
        self.ccy1 = ccy1
        self.ccy2 = ccy2
        self.asof = asof

        ## Set the message:
        super().__init__(f"Foreign exchange rate for {ccy1}/{ccy2} not found as of {asof}")


class FXRate(NamedTuple):
    """
    Defines a foreign exchange (FX) rate model.

    Note that the constructor of this class is not safe: It does not check input. :method:`FXRate.of`, on the
    other hand provides a safer way of creating :class:`FXRate` instances.

    **Implementation Note:**

    I wanted to use an immutable, compact object model with fast creation and property access. Options were
    tweaked plain-vanilla Python class, NamedTuple and dataclasses.

    NamedTuple has slightly slower property access, whereby immutable dataclasses are slow for creation.

    Furthermore, as of the implementation of this class, mypy does not have proper dataclass support. Therefore,
    I am sticking to NamedTuple implementation.

    Last but not least, as objects are essentially tuples, indexed access to properties is possible and slightly
    faster.

    >>> import datetime
    >>> from decimal import Decimal
    >>> from pypara.currencies import Currencies
    >>> rate = FXRate(Currencies["EUR"], Currencies["USD"], datetime.date.today(), Decimal("2"))
    >>> ccy1, ccy2, date, value = rate
    >>> ccy1 == Currencies["EUR"]
    True
    >>> ccy2 == Currencies["USD"]
    True
    >>> date == datetime.date.today()
    True
    >>> value == Decimal("2")
    True
    """

    #: Defines the first currency of the FX rate.
    ccy1: Currency

    #: Defines the second currency of the FX rate.
    ccy2: Currency

    #: Defines the date the FX rate is effective as of.
    date: Date

    #: Defines the value of the FX rate.
    value: Decimal

    def __invert__(self) -> "FXRate":
        """
        Returns the inverted foreign exchange rate.

        >>> import datetime
        >>> from decimal import Decimal
        >>> from pypara.currencies import Currencies
        >>> nrate = FXRate(Currencies["EUR"], Currencies["USD"], datetime.date.today(), Decimal("2"))
        >>> rrate = FXRate(Currencies["USD"], Currencies["EUR"], datetime.date.today(), Decimal("0.5"))
        >>> ~nrate == rrate
        True
        """
        return FXRate(self[1], self[0], self[2], self[3] ** -1)

    @classmethod
    def of(cls, ccy1: Currency, ccy2: Currency, date: Date, value: Decimal) -> "FXRate":
        """
        Creates and returns an FX rate instance by validating arguments.

        >>> import datetime
        >>> from decimal import Decimal
        >>> from pypara.currencies import Currencies
        >>> urate = FXRate(Currencies["EUR"], Currencies["USD"], datetime.date.today(), Decimal("2"))
        >>> srate = FXRate.of(Currencies["EUR"], Currencies["USD"], datetime.date.today(), Decimal("2"))
        >>> urate == srate
        True
        """
        ## All argument must be of the respective specified type:
        if not isinstance(ccy1, Currency):
            raise ValueError("CCY/1 must be of type `Currency`.")
        if not isinstance(ccy2, Currency):
            raise ValueError("CCY/2 must be of type `Currency`.")
        if not isinstance(ccy1, Currency):
            raise ValueError("FX rate value must be of type `Decimal`.")
        if not isinstance(ccy1, Currency):
            raise ValueError("FX rate date must be of type `date`.")

        ## Check the value:
        if value <= ZERO:
            raise ValueError("FX rate value can not be equal to or less than `zero`.")

        ## Check consistency:
        if ccy1 == ccy2 and value != ONE:
            raise ValueError("FX rate to the same currency must be `one`.")

        ## Create and return the FX rate instance:
        return cls(ccy1, ccy2, date, value)


class FXRateService(metaclass=ABCMeta):
    """
    Provides an abstract class for serving foreign exchange rates.
    """

    #: Defines the default foreign exchange rate service for the runtime.
    default: Optional["FXRateService"] = None  # noqa: E704

    #: Defines an FX rate query tuple.
    TQuery = Tuple[Currency, Currency, Date]

    @abstractmethod
    def query(self, ccy1: Currency, ccy2: Currency, asof: Date, strict: bool = False) -> Optional[FXRate]:
        """
        Returns the foreign exchange rate of a given currency pair as of a given date.

        :param ccy1: The first currency of foreign exchange rate.
        :param ccy2: The second currency of foreign exchange rate.
        :param asof: Temporal dimension the foreign exchange rate is effective as of.
        :param strict: Indicates if we should raise a lookup error if that the foreign exchange rate can not be found.
        :return: The foreign exhange rate as a :class:`Decimal` instance or None.
        """
        pass

    @abstractmethod
    def queries(self, queries: Iterable[TQuery], strict: bool = False) -> Iterable[Optional[FXRate]]:
        """
        Returns foreign exchange rates for a given collection of currency pairs and dates.

        :param queries: An iterable of :class:`Currency`, :class:`Currency` and :class:`Temporal` tuples.
        :param strict: Indicates if we should raise a lookup error if that the foreign exchange rate can not be found.
        :return: An iterable of rates.
        """
        pass
