"""
This module provides definitions and functionality related to encoding monetary values and operating on them.
"""

__all__ = [
    "IncompatibleCurrencyError",
    "MonetaryOperationException",
    "Money",
    "NoMoney",
    "NoPrice",
    "NoneMoney",
    "NonePrice",
    "Price",
    "SomeMoney",
    "SomePrice",
]

from abc import abstractmethod
from decimal import Decimal, DivisionByZero, InvalidOperation
from typing import Any, NamedTuple, Optional, Union, overload

from .commons.errors import ProgrammingError
from .commons.numbers import Numeric
from .commons.zeitgeist import Date
from .currencies import Currency
from .exchange import FXRateLookupError, FXRateService


class IncompatibleCurrencyError(ValueError):
    """
    Provides an exception indicating that there is an attempt for performing monetary operations
    with incompatible currencies.
    """

    def __init__(self, ccy1: Currency, ccy2: Currency, operation: str = "<Unspecified>") -> None:
        """
        Initializes an incompatible currency error message.
        """
        ## Keep sloys:
        self.ccy1 = ccy1
        self.ccy2 = ccy2
        self.operation = operation

        ## Call super:
        super().__init__(f"{ccy1.code} vs {ccy2.code} are incompatible for operation '{operation}'.")


class MonetaryOperationException(TypeError):
    """
    Provides an exception that a certain monetary operation can not be carried on.
    """

    pass


class Money:
    """
    Provides an abstract money model and its semantics.
    """

    ## No need for slots.
    __slots__ = ()

    #: Defines the *undefined* money object as a singleton.
    NA: "Money"

    #: Returns the currency of the money object, if defined.
    #:
    #: Note that a :class:`TypeError` is raised if call-site attempts to access this property of an undefined money.
    ccy: Currency

    #: Returns the quantity of the money object, if defined.
    #:
    #: Note that a :class:`TypeError` is raised if call-site attempts to access this property of an undefined money.
    qty: Decimal

    #: Returns the value date of the money object, if defined.
    #:
    #: Note that a :class:`TypeError` is raised if call-site attempts to access this property of an undefined money.
    dov: Date

    #: Indicates that the money is a *defined* monetary value.
    defined: bool  # noqa: E704

    #: Indicates that the money is an *undefined* monetary value.
    undefined: bool

    @abstractmethod
    def is_equal(self, other: Any) -> bool:
        """
        Checks the equality of two money objects.

        In particular:

        1. ``True`` if ``other`` is a money object **and** all slots are same.
        2. ``False`` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def as_boolean(self) -> bool:
        """
        Returns the logical representation of the money object.

        In particular:

        1. ``False`` if money is *undefined* **or** money quantity is ``zero``.
        2. ``True`` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def as_float(self) -> float:
        """
        Returns the quantity as a ``float`` if *defined*, raises class:`MonetaryOperationException` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def as_integer(self) -> int:
        """
        Returns the quantity as an ``int`` if *defined*, raises class:`MonetaryOperationException` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def abs(self) -> "Money":
        """
        Returns the absolute money if *defined*, itself otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def negative(self) -> "Money":
        """
        Negates the quantity of the monetary value if *defined*, itself otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def positive(self) -> "Money":
        """
        Returns same monetary value if *defined*, itself otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def round(self, ndigits: int = 0) -> "Money":
        """
        Rounds the quantity of the monetary value to ``ndigits`` by using ``HALF_EVEN`` method if *defined*, itself
        otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def add(self, other: "Money") -> "Money":
        """
        Performs monetary addition on the money object and the given ``other`` money object.

        Note that::

        1. Raises :class:`IncompatibleCurrencyError` if currencies do not match.
        2. If any of the operands are undefined, returns the other one conveniently.
        3. Dates are carried forward as a result of addition of two defined money objects.
        """
        raise NotImplementedError

    @abstractmethod
    def scalar_add(self, other: Numeric) -> "Money":
        """
        Performs scalar addition on the quantity of the money.

        Note that undefined money object is returned as is.
        """
        raise NotImplementedError

    @abstractmethod
    def subtract(self, other: "Money") -> "Money":
        """
        Performs monetary subtraction on the money object and the given ``other`` money object.

        Note that::

        1. Raises :class:`IncompatibleCurrencyError` if currencies do not match.
        2. If any of the operands are undefined, returns the other one conveniently.
        3. Dates are carried forward as a result of addition of two defined money objects.
        """
        raise NotImplementedError

    @abstractmethod
    def scalar_subtract(self, other: Numeric) -> "Money":
        """
        Performs scalar subtraction on the quantity of the money.

        Note that undefined money object is returned as is.
        """
        raise NotImplementedError

    @abstractmethod
    def multiply(self, other: Numeric) -> "Money":
        """
        Performs scalar multiplication.

        Note that undefined money object is returned as is.
        """
        raise NotImplementedError

    @abstractmethod
    def divide(self, other: Numeric) -> "Money":
        """
        Performs ordinary division on the money object if *defined*, itself otherwise.

        Note that division by zero yields an undefined money object.
        """
        raise NotImplementedError

    @abstractmethod
    def floor_divide(self, other: Numeric) -> "Money":
        """
        Performs floor division on the money object if *defined*, itself otherwise.

        Note that division by zero yields an undefined money object.

        """
        raise NotImplementedError

    @abstractmethod
    def lt(self, other: "Money") -> bool:
        """
        Applies "less than" comparison against ``other`` money.

        Note that::

        1. Undefined money objects are always less than ``other`` if ``other`` is not undefined, and
        2. :class:`IncompatibleCurrencyError` is raised when comparing two defined money objects with different
        currencies.
        """
        pass

    @abstractmethod
    def lte(self, other: "Money") -> bool:
        """
        Applies "less than or equal to" comparison against ``other`` money.

        Note that::

        1. Undefined money objects are always less than or equal to ``other``, and
        2. :class:`IncompatibleCurrencyError` is raised when comparing two defined money objects with different
        currencies.
        """
        pass

    @abstractmethod
    def gt(self, other: "Money") -> bool:
        """
        Applies "greater than" comparison against ``other`` money.

        Note that::

        1. Undefined money objects are never greater than ``other``,
        2. Defined money objects are always greater than ``other`` if other is undefined, and
        3. :class:`IncompatibleCurrencyError` is raised when comparing two defined money objects with different
        currencies.
        """
        pass

    @abstractmethod
    def gte(self, other: "Money") -> bool:
        """
        Applies "greater than or equal to" comparison against ``other`` money.

        Note that::

        1. Undefined money objects are never greater than or equal to ``other`` if ``other`` is defined,
        2. Undefined money objects are greater than or equal to ``other`` if ``other is undefined, and
        3. :class:`IncompatibleCurrencyError` is raised when comparing two defined money objects with different
        currencies.
        """
        pass

    @abstractmethod
    def with_ccy(self, ccy: Currency) -> "Money":
        """
        Creates a new money object with the given currency if money is *defined*, returns itself otherwise.
        """
        pass

    @abstractmethod
    def with_qty(self, qty: Decimal) -> "Money":
        """
        Creates a new money object with the given quantity if money is *defined*, returns itself otherwise.
        """
        pass

    @abstractmethod
    def with_dov(self, dov: Date) -> "Money":
        """
        Creates a new money object with the given value date if money is *defined*, returns itself otherwise.
        """
        pass

    @abstractmethod
    def convert(self, to: Currency, asof: Optional[Date] = None, strict: bool = False) -> "Money":
        """
        Converts the monetary value from one currency to another.

        Raises :class:`FXRateLookupError` if no foreign exchange rate can be found for conversion.

        Note that we will carry the date forward as per ``asof`` date.
        """
        raise NotImplementedError

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[Date]) -> "Money":
        """
        Provides a factory method to create a new money object in a safe manner.
        """
        if qty is None or ccy is None or dov is None:
            return NoMoney
        return SomeMoney(ccy, ccy.quantize(qty), dov)

    @property
    @abstractmethod
    def price(self) -> "Price":
        """
        Returns the price representation of the money object.
        """
        raise NotImplementedError

    @abstractmethod
    def __bool__(self) -> bool:
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __abs__(self) -> "Money":
        pass

    @abstractmethod
    def __float__(self) -> float:
        pass

    @abstractmethod
    def __int__(self) -> int:
        pass

    @overload
    def __round__(self) -> int:
        ...

    @overload
    def __round__(self, ndigits: None) -> int:
        ...

    @overload
    def __round__(self, ndigits: int) -> "Money":
        ...

    def __round__(self, ndigits: Optional[int] = 0) -> Union["Money", int]:
        return self.round(ndigits or 0)

    @abstractmethod
    def __neg__(self) -> "Money":
        pass

    @abstractmethod
    def __pos__(self) -> "Money":
        pass

    @abstractmethod
    def __add__(self, other: "Money") -> "Money":
        pass

    @abstractmethod
    def __sub__(self, other: "Money") -> "Money":
        pass

    @abstractmethod
    def __mul__(self, other: Numeric) -> "Money":
        pass

    @abstractmethod
    def __truediv__(self, other: Numeric) -> "Money":
        pass

    @abstractmethod
    def __floordiv__(self, other: Numeric) -> "Money":
        pass

    @abstractmethod
    def __lt__(self, other: "Money") -> bool:
        pass

    @abstractmethod
    def __le__(self, other: "Money") -> bool:
        pass

    @abstractmethod
    def __gt__(self, other: "Money") -> bool:
        pass

    @abstractmethod
    def __ge__(self, other: "Money") -> bool:
        pass


class SomeMoney(Money, NamedTuple("SomeMoney", [("ccy", Currency), ("qty", Decimal), ("dov", Date)])):
    """
    Provides a *defined* money object model.
    """

    __slots__ = ()

    defined = True

    undefined = False

    def is_equal(self, other: Any) -> bool:
        return other.__class__ is SomeMoney and tuple(self) == tuple(other)

    def as_boolean(self) -> bool:
        return self[1].__bool__()

    def as_float(self) -> float:
        return self[1].__float__()

    def as_integer(self) -> int:
        return self[1].__int__()

    def abs(self) -> "Money":
        c, q, d = self
        return SomeMoney(c, q.__abs__(), d)

    def negative(self) -> "Money":
        c, q, d = self
        return SomeMoney(c, q.__neg__(), d)

    def positive(self) -> "Money":
        c, q, d = self
        return SomeMoney(c, q.__pos__(), d)

    def round(self, ndigits: int = 0) -> "Money":
        c, q, d = self
        dec = c.decimals
        return SomeMoney(c, q.__round__(ndigits if ndigits < dec else dec), d)

    def add(self, other: "Money") -> "Money":
        if other.undefined:
            return self

        c1: Currency
        q1: Decimal
        d1: Date
        c2: Currency
        q2: Decimal
        d2: Date
        c1, q1, d1 = self
        c2, q2, d2 = other  # type: ignore

        if c1 != c2:
            raise IncompatibleCurrencyError(ccy1=c1, ccy2=c2, operation="addition")

        return SomeMoney(c1, q1 + q2, d1 if d1 > d2 else d2)

    def scalar_add(self, other: Numeric) -> "Money":
        ## TODO: **try** not casting other to Decimal.
        c, q, d = self
        return SomeMoney(c, (q + Decimal(other)).quantize(c.quantizer), d)

    def subtract(self, other: "Money") -> "Money":
        if other.undefined:
            return self

        c1: Currency
        q1: Decimal
        d1: Date
        c2: Currency
        q2: Decimal
        d2: Date
        c1, q1, d1 = self
        c2, q2, d2 = other  # type: ignore

        if c1 != c2:
            raise IncompatibleCurrencyError(ccy1=c1, ccy2=c2, operation="subtraction")

        return SomeMoney(c1, q1 - q2, d1 if d1 > d2 else d2)

    def scalar_subtract(self, other: Numeric) -> "Money":
        ## TODO: **try** not casting other to Decimal.
        c, q, d = self
        return SomeMoney(c, (q - Decimal(other)).quantize(c.quantizer), d)

    def multiply(self, other: Numeric) -> "Money":
        ## TODO: **try** not casting other to Decimal.
        c, q, d = self
        return SomeMoney(c, (q * Decimal(other)).quantize(c.quantizer), d)

    def divide(self, other: Numeric) -> "Money":
        ## TODO: **try** not casting other to Decimal.
        try:
            c, q, d = self
            return SomeMoney(c, (q / Decimal(other)).quantize(c.quantizer), d)
        except (InvalidOperation, DivisionByZero):
            return NoMoney

    def floor_divide(self, other: Numeric) -> "Money":
        ## TODO: **try** not casting other to Decimal.
        try:
            c, q, d = self
            return SomeMoney(c, (q // Decimal(other)).quantize(c.quantizer), d)
        except (InvalidOperation, DivisionByZero):
            return NoMoney

    def lt(self, other: "Money") -> bool:
        if other.undefined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation="< comparision")
        return self.qty < other.qty

    def lte(self, other: "Money") -> bool:
        if other.undefined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation="<= comparision")
        return self.qty <= other.qty

    def gt(self, other: "Money") -> bool:
        if other.undefined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation="> comparision")
        return self.qty > other.qty

    def gte(self, other: "Money") -> bool:
        if other.undefined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation=">= comparision")
        return self.qty >= other.qty

    def with_ccy(self, ccy: Currency) -> "Money":
        return SomeMoney(ccy, self[1], self[2])

    def with_qty(self, qty: Decimal) -> "Money":
        c, q, d = self
        return SomeMoney(c, qty.quantize(c.quantizer), d)

    def with_dov(self, dov: Date) -> "Money":
        return SomeMoney(self[0], self[1], dov)

    def convert(self, to: Currency, asof: Optional[Date] = None, strict: bool = False) -> "Money":
        ## Get slots:
        ccy, qty, dov = self

        ## Get date of conversion:
        asof = asof or dov

        ## Attempt to get the FX rate:
        try:
            rate = FXRateService.default.query(ccy, to, asof, strict)  # type: ignore
        except AttributeError as exc:
            if FXRateService.default is None:
                raise ProgrammingError("Did you implement and set the default FX rate service?")
            else:
                raise exc

        ## Do we have a rate?
        if rate is None:
            ## Nope, shall we raise exception?
            if strict:
                ## Yep:
                raise FXRateLookupError(ccy, to, asof)
            else:
                ## Just return NA:
                return NoMoney

        ## Compute and return:
        return SomeMoney(to, (qty * rate.value).quantize(to.quantizer), asof)

    @property
    def price(self) -> "Price":
        return SomePrice(*self)

    __bool__ = as_boolean

    __eq__ = is_equal

    __abs__ = abs

    __float__ = as_float

    __int__ = as_integer

    __neg__ = negative

    __pos__ = positive

    __add__ = add  # type: ignore

    __sub__ = subtract

    __mul__ = multiply  # type: ignore

    __truediv__ = divide

    __floordiv__ = floor_divide

    __lt__ = lt  # type: ignore

    __le__ = lte  # type: ignore

    __gt__ = gt  # type: ignore

    __ge__ = gte  # type: ignore


class NoneMoney(Money):

    __slots__ = ()

    defined = False

    undefined = True

    def as_boolean(self) -> bool:
        return False

    def is_equal(self, other: Any) -> bool:
        return other.__class__ is NoneMoney

    def abs(self) -> "Money":
        return self

    def as_float(self) -> float:
        raise TypeError("Undefined monetary values do not have quantity information.")

    def as_integer(self) -> int:
        raise TypeError("Undefined monetary values do not have quantity information.")

    def round(self, ndigits: int = 0) -> "Money":
        return self

    def negative(self) -> "Money":
        return self

    def positive(self) -> "Money":
        return self

    def add(self, other: "Money") -> "Money":
        return other

    def scalar_add(self, other: Numeric) -> "Money":
        return self

    def subtract(self, other: "Money") -> "Money":
        return -other

    def scalar_subtract(self, other: Numeric) -> "Money":
        return self

    def multiply(self, other: Numeric) -> "Money":
        return self

    def divide(self, other: Numeric) -> "Money":
        return self

    def floor_divide(self, other: Numeric) -> "Money":
        return self

    def lt(self, other: "Money") -> bool:
        return other.defined

    def lte(self, other: "Money") -> bool:
        return True

    def gt(self, other: "Money") -> bool:
        return False

    def gte(self, other: "Money") -> bool:
        return other.undefined

    def with_ccy(self, ccy: Currency) -> "Money":
        return self

    def with_qty(self, qty: Decimal) -> "Money":
        return self

    def with_dov(self, dov: Date) -> "Money":
        return self

    def convert(self, to: Currency, asof: Optional[Date] = None, strict: bool = False) -> "Money":
        return self

    @property
    def price(self) -> "Price":
        return NoPrice

    __bool__ = as_boolean

    __eq__ = is_equal

    __abs__ = abs

    __float__ = as_float

    __int__ = as_integer

    __neg__ = negative

    __pos__ = positive

    __add__ = add

    __sub__ = subtract

    __mul__ = multiply

    __truediv__ = divide

    __floordiv__ = floor_divide

    __lt__ = lt

    __le__ = lte

    __gt__ = gt

    __ge__ = gte


## Define and attach undefined money singleton.
Money.NA = NoMoney = NoneMoney()


class Price:
    """
    Provides an abstract price model and its semantics.
    """

    ## No need for slots.
    __slots__ = ()

    #: Defines the *undefined* price object as a singleton.
    NA: "Price"

    #: Returns the currency of the price object, if defined.
    #:
    #: Note that a :class:`TypeError` is raised if call-site attempts to access this property of an undefined price.
    ccy: Currency

    #: Returns the quantity of the price object, if defined.
    #:
    #: Note that a :class:`TypeError` is raised if call-site attempts to access this property of an undefined price.
    qty: Decimal

    #: Returns the value date of the price object, if defined.
    #:
    #: Note that a :class:`TypeError` is raised if call-site attempts to access this property of an undefined price.
    dov: Date

    #: Indicates that the price is a *defined* monetary value.
    defined: bool  # noqa: E704

    #: Indicates that the price is an *undefined* monetary value.
    undefined: bool

    @abstractmethod
    def is_equal(self, other: Any) -> bool:
        """
        Checks the equality of two price objects.

        In particular:

        1. ``True`` if ``other`` is a price object **and** all slots are same.
        2. ``False`` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def as_boolean(self) -> bool:
        """
        Returns the logical representation of the price object.

        In particular:

        1. ``False`` if price is *undefined* **or** price quantity is ``zero``.
        2. ``True`` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def as_float(self) -> float:
        """
        Returns the quantity as a ``float`` if *defined*, raises class:`MonetaryOperationException` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def as_integer(self) -> int:
        """
        Returns the quantity as an ``int`` if *defined*, raises class:`MonetaryOperationException` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def abs(self) -> "Price":
        """
        Returns the absolute price if *defined*, itself otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def negative(self) -> "Price":
        """
        Negates the quantity of the monetary value if *defined*, itself otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def positive(self) -> "Price":
        """
        Returns same monetary value if *defined*, itself otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def round(self, ndigits: int = 0) -> "Price":
        """
        Rounds the quantity of the monetary value to ``ndigits`` by using ``HALF_EVEN`` method if *defined*, itself
        otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def add(self, other: "Price") -> "Price":
        """
        Performs monetary addition on the price object and the given ``other`` price object.

        Note that::

        1. Raises :class:`IncompatibleCurrencyError` if currencies do not match.
        2. If any of the operands are undefined, returns the other one conveniently.
        3. Dates are carried forward as a result of addition of two defined price objects.
        """
        raise NotImplementedError

    @abstractmethod
    def scalar_add(self, other: Numeric) -> "Price":
        """
        Performs scalar addition on the quantity of the price.

        Note that undefined price object is returned as is.
        """
        raise NotImplementedError

    @abstractmethod
    def subtract(self, other: "Price") -> "Price":
        """
        Performs monetary subtraction on the price object and the given ``other`` price object.

        Note that::

        1. Raises :class:`IncompatibleCurrencyError` if currencies do not match.
        2. If any of the operands are undefined, returns the other one conveniently.
        3. Dates are carried forward as a result of addition of two defined price objects.
        """
        raise NotImplementedError

    @abstractmethod
    def scalar_subtract(self, other: Numeric) -> "Price":
        """
        Performs scalar subtraction on the quantity of the price.

        Note that undefined price object is returned as is.
        """
        raise NotImplementedError

    @abstractmethod
    def multiply(self, other: Numeric) -> "Price":
        """
        Performs scalar multiplication.

        Note that undefined price object is returned as is.
        """
        raise NotImplementedError

    @abstractmethod
    def times(self, other: Numeric) -> "Money":
        """
        Performs monetary multiplication operation.

        Note that undefined price object is returned as is.
        """
        raise NotImplementedError

    @abstractmethod
    def divide(self, other: Numeric) -> "Price":
        """
        Performs ordinary division on the price object if *defined*, itself otherwise.

        Note that division by zero yields an undefined price object.
        """
        raise NotImplementedError

    @abstractmethod
    def floor_divide(self, other: Numeric) -> "Price":
        """
        Performs floor division on the price object if *defined*, itself otherwise.

        Note that division by zero yields an undefined price object.

        """
        raise NotImplementedError

    @abstractmethod
    def lt(self, other: "Price") -> bool:
        """
        Applies "less than" comparison against ``other`` price.

        Note that::

        1. Undefined price objects are always less than ``other`` if ``other`` is not undefined, and
        2. :class:`IncompatibleCurrencyError` is raised when comparing two defined price objects with different
        currencies.
        """
        pass

    @abstractmethod
    def lte(self, other: "Price") -> bool:
        """
        Applies "less than or equal to" comparison against ``other`` price.

        Note that::

        1. Undefined price objects are always less than or equal to ``other``, and
        2. :class:`IncompatibleCurrencyError` is raised when comparing two defined price objects with different
        currencies.
        """
        pass

    @abstractmethod
    def gt(self, other: "Price") -> bool:
        """
        Applies "greater than" comparison against ``other`` price.

        Note that::

        1. Undefined price objects are never greater than ``other``,
        2. Defined price objects are always greater than ``other`` if other is undefined, and
        3. :class:`IncompatibleCurrencyError` is raised when comparing two defined price objects with different
        currencies.
        """
        pass

    @abstractmethod
    def gte(self, other: "Price") -> bool:
        """
        Applies "greater than or equal to" comparison against ``other`` price.

        Note that::

        1. Undefined price objects are never greater than or equal to ``other`` if ``other`` is defined,
        2. Undefined price objects are greater than or equal to ``other`` if ``other is undefined, and
        3. :class:`IncompatibleCurrencyError` is raised when comparing two defined price objects with different
        currencies.
        """
        pass

    @abstractmethod
    def with_ccy(self, ccy: Currency) -> "Price":
        """
        Creates a new price object with the given currency if price is *defined*, returns itself otherwise.
        """
        pass

    @abstractmethod
    def with_qty(self, qty: Decimal) -> "Price":
        """
        Creates a new price object with the given quantity if price is *defined*, returns itself otherwise.
        """
        pass

    @abstractmethod
    def with_dov(self, dov: Date) -> "Price":
        """
        Creates a new price object with the given value date if price is *defined*, returns itself otherwise.
        """
        pass

    @abstractmethod
    def convert(self, to: Currency, asof: Optional[Date] = None, strict: bool = False) -> "Price":
        """
        Converts the monetary value from one currency to another.

        Raises :class:`FXRateLookupError` if no foreign exchange rate can be found for conversion.

        Note that we will carry the date forward as per ``asof`` date.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def money(self) -> Money:
        """
        Returns the money representation of the price object.
        """
        raise NotImplementedError

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[Date]) -> "Price":
        """
        Provides a factory method to create a new price object in a safe manner.
        """
        if qty is None or ccy is None or dov is None:
            return NoPrice
        return SomePrice(ccy, qty, dov)

    @abstractmethod
    def __bool__(self) -> bool:
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __abs__(self) -> "Price":
        pass

    @abstractmethod
    def __float__(self) -> float:
        pass

    @abstractmethod
    def __int__(self) -> int:
        pass

    @overload
    def __round__(self) -> int:
        ...

    @overload
    def __round__(self, ndigits: None) -> int:
        ...

    @overload
    def __round__(self, ndigits: int) -> "Price":
        ...

    def __round__(self, ndigits: Optional[int] = 0) -> Union["Price", int]:
        return self.round(ndigits or 0)

    @abstractmethod
    def __neg__(self) -> "Price":
        pass

    @abstractmethod
    def __pos__(self) -> "Price":
        pass

    @abstractmethod
    def __add__(self, other: "Price") -> "Price":
        pass

    @abstractmethod
    def __sub__(self, other: "Price") -> "Price":
        pass

    @abstractmethod
    def __mul__(self, other: Numeric) -> "Price":
        pass

    @abstractmethod
    def __truediv__(self, other: Numeric) -> "Price":
        pass

    @abstractmethod
    def __floordiv__(self, other: Numeric) -> "Price":
        pass

    @abstractmethod
    def __lt__(self, other: "Price") -> bool:
        pass

    @abstractmethod
    def __le__(self, other: "Price") -> bool:
        pass

    @abstractmethod
    def __gt__(self, other: "Price") -> bool:
        pass

    @abstractmethod
    def __ge__(self, other: "Price") -> bool:
        pass


class SomePrice(Price, NamedTuple("SomePrice", [("ccy", Currency), ("qty", Decimal), ("dov", Date)])):
    """
    Provides a *defined* price object model.
    """

    __slots__ = ()

    defined = True

    undefined = False

    def is_equal(self, other: Any) -> bool:
        return other.__class__ is SomePrice and tuple(self) == tuple(other)

    def as_boolean(self) -> bool:
        return self.qty.__bool__()

    def as_float(self) -> float:
        return self.qty.__float__()

    def as_integer(self) -> int:
        return self.qty.__int__()

    def abs(self) -> "Price":
        c, q, d = self
        return SomePrice(c, q.__abs__(), d)

    def negative(self) -> "Price":
        c, q, d = self
        return SomePrice(c, q.__neg__(), d)

    def positive(self) -> "Price":
        c, q, d = self
        return SomePrice(c, q.__pos__(), d)

    def round(self, ndigits: int = 0) -> "Price":
        c, q, d = self
        return SomePrice(c, q.__round__(ndigits), d)

    def add(self, other: "Price") -> "Price":
        if other.undefined:
            return self

        c1: Currency
        q1: Decimal
        d1: Date
        c2: Currency
        q2: Decimal
        d2: Date
        c1, q1, d1 = self
        c2, q2, d2 = other  # type: ignore

        if c1 != c2:
            raise IncompatibleCurrencyError(ccy1=c1, ccy2=c2, operation="addition")

        return SomePrice(c1, q1 + q2, d1 if d1 > d2 else d2)

    def scalar_add(self, other: Numeric) -> "Price":
        ## TODO: **try** not casting other to Decimal.
        c, q, d = self
        return SomePrice(c, q + Decimal(other), d)

    def subtract(self, other: "Price") -> "Price":
        if other.undefined:
            return self

        c1: Currency
        q1: Decimal
        d1: Date
        c2: Currency
        q2: Decimal
        d2: Date
        c1, q1, d1 = self
        c2, q2, d2 = other  # type: ignore

        if c1 != c2:
            raise IncompatibleCurrencyError(ccy1=c1, ccy2=c2, operation="subtraction")

        return SomePrice(c1, q1 - q2, d1 if d1 > d2 else d2)

    def scalar_subtract(self, other: Numeric) -> "Price":
        ## TODO: **try** not casting other to Decimal.
        c, q, d = self
        return SomePrice(c, q - Decimal(other), d)

    def multiply(self, other: Numeric) -> "Price":
        ## TODO: **try** not casting other to Decimal.
        c, q, d = self
        return SomePrice(c, q * Decimal(other), d)

    def times(self, other: Numeric) -> "Money":
        c, q, d = self
        return SomeMoney(c, (q * Decimal(other)).quantize(c.quantizer), self.dov)

    def divide(self, other: Numeric) -> "Price":
        ## TODO: **try** not casting other to Decimal.
        try:
            c, q, d = self
            return SomePrice(c, q / Decimal(other), d)
        except (InvalidOperation, DivisionByZero):
            return NoPrice

    def floor_divide(self, other: Numeric) -> "Price":
        ## TODO: **try** not casting other to Decimal.
        try:
            c, q, d = self
            return SomePrice(c, q // Decimal(other), d)
        except (InvalidOperation, DivisionByZero):
            return NoPrice

    def lt(self, other: "Price") -> bool:
        if other.undefined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation="< comparision")
        return self.qty < other.qty

    def lte(self, other: "Price") -> bool:
        if other.undefined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation="<= comparision")
        return self.qty <= other.qty

    def gt(self, other: "Price") -> bool:
        if other.undefined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation="> comparision")
        return self.qty > other.qty

    def gte(self, other: "Price") -> bool:
        if other.undefined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(ccy1=self.ccy, ccy2=other.ccy, operation=">= comparision")
        return self.qty >= other.qty

    def with_ccy(self, ccy: Currency) -> "Price":
        return SomePrice(ccy, self[1], self[2])

    def with_qty(self, qty: Decimal) -> "Price":
        return SomePrice(self[0], qty, self[2])

    def with_dov(self, dov: Date) -> "Price":
        return SomePrice(self[0], self[1], dov)

    def convert(self, to: Currency, asof: Optional[Date] = None, strict: bool = False) -> "Price":
        ## Get slots:
        ccy, qty, dov = self

        ## Get date of conversion:
        asof = asof or dov

        ## Attempt to get the FX rate:
        try:
            rate = FXRateService.default.query(ccy, to, asof, strict)  # type: ignore
        except AttributeError as exc:
            if FXRateService.default is None:
                raise ProgrammingError("Did you implement and set the default FX rate service?")
            else:
                raise exc

        ## Do we have a rate?
        if rate is None:
            ## Nope, shall we raise exception?
            if strict:
                ## Yep:
                raise FXRateLookupError(ccy, to, asof)
            else:
                ## Just return NA:
                return NoPrice

        ## Compute and return:
        return SomePrice(to, qty * rate.value, asof)

    @property
    def money(self) -> Money:
        c, q, d = self
        return SomeMoney(c, q.quantize(c.quantizer), d)

    __bool__ = as_boolean

    __eq__ = is_equal

    __abs__ = abs

    __float__ = as_float

    __int__ = as_integer

    __neg__ = negative

    __pos__ = positive

    __add__ = add  # type: ignore

    __sub__ = subtract

    __mul__ = multiply  # type: ignore

    __truediv__ = divide

    __floordiv__ = floor_divide

    __lt__ = lt  # type: ignore

    __le__ = lte  # type: ignore

    __gt__ = gt  # type: ignore

    __ge__ = gte  # type: ignore


class NonePrice(Price):

    __slots__ = ()

    defined = False

    undefined = True

    def as_boolean(self) -> bool:
        return False

    def is_equal(self, other: Any) -> bool:
        return other.__class__ is NonePrice

    def abs(self) -> "Price":
        return self

    def as_float(self) -> float:
        raise TypeError("Undefined monetary values do not have quantity information.")

    def as_integer(self) -> int:
        raise TypeError("Undefined monetary values do not have quantity information.")

    def round(self, ndigits: int = 0) -> "Price":
        return self

    def negative(self) -> "Price":
        return self

    def positive(self) -> "Price":
        return self

    def add(self, other: "Price") -> "Price":
        return other

    def scalar_add(self, other: Numeric) -> "Price":
        return self

    def subtract(self, other: "Price") -> "Price":
        return -other

    def scalar_subtract(self, other: Numeric) -> "Price":
        return self

    def multiply(self, other: Numeric) -> "Price":
        return self

    def times(self, other: Numeric) -> "Money":
        return NoMoney

    def divide(self, other: Numeric) -> "Price":
        return self

    def floor_divide(self, other: Numeric) -> "Price":
        return self

    def lt(self, other: "Price") -> bool:
        return other.defined

    def lte(self, other: "Price") -> bool:
        return True

    def gt(self, other: "Price") -> bool:
        return False

    def gte(self, other: "Price") -> bool:
        return other.undefined

    def with_ccy(self, ccy: Currency) -> "Price":
        return self

    def with_qty(self, qty: Decimal) -> "Price":
        return self

    def with_dov(self, dov: Date) -> "Price":
        return self

    def convert(self, to: Currency, asof: Optional[Date] = None, strict: bool = False) -> "Price":
        return self

    money = NoMoney

    __bool__ = as_boolean

    __eq__ = is_equal

    __abs__ = abs

    __float__ = as_float

    __int__ = as_integer

    __neg__ = negative

    __pos__ = positive

    __add__ = add

    __sub__ = subtract

    __mul__ = multiply

    __truediv__ = divide

    __floordiv__ = floor_divide

    __lt__ = lt

    __le__ = lte

    __gt__ = gt

    __ge__ = gte


## Define and attach undefined price singleton.
Price.NA = NoPrice = NonePrice()
