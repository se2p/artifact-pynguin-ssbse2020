"""
This module provides day-count convention definitions and functionlity.
"""

__all__ = ["DCC", "DCCRegistry"]

import calendar
import datetime
from decimal import Decimal
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Set, Union

from dateutil.relativedelta import relativedelta

from .commons.numbers import ONE, ZERO
from .commons.zeitgeist import Date
from .currencies import Currencies, Currency
from .monetary import Money

#: Defines a type alias for day count fraction calculation functions.
DCFC = Callable[[Date, Date, Date, Optional[Decimal]], Decimal]


def _as_ccys(codes: Set[str]) -> Set[Currency]:
    """
    Converts a set of currency codes to a set of currencies.
    """
    return {Currencies[c] for c in codes}


def _get_date_range(start: Date, end: Date) -> Iterable[Date]:
    """
    Returns a generator of dates falling into range within the given period (``end`` is exclusive).

    :param start: The start date of the period.
    :param end: The end date of the period.
    :return: A generator of dates.
    """
    for i in range((end - start).days):
        yield start + datetime.timedelta(days=i)


def _get_actual_day_count(start: Date, end: Date) -> int:
    """
    Counts the actual number of days in the given period.

    :param start: The start date of the period.
    :param end: The end date of the period.
    :return: The number of days in the given period.

    >>> _get_actual_day_count(datetime.date(2017, 1, 1), datetime.date(2017, 1, 1))
    0
    >>> _get_actual_day_count(datetime.date(2017, 1, 1), datetime.date(2017, 1, 2))
    1
    """
    return (end - start).days


def _has_leap_day(start: Date, end: Date) -> bool:
    """
    Indicates if the range has any leap day.
    """
    ## Get all leap years:
    years = {year for year in range(start.year, end.year + 1) if calendar.isleap(year)}

    ## Check if any of the lap day falls in our range:
    for year in years:
        ## Construct the leap day:
        leapday = datetime.date(year, 2, 29)

        ## Is the leap date in the range?
        if start <= leapday <= end:
            ## Yes, the leap day is within the date range. Return True:
            return True

    ## No leap day in the range, return False:
    return False


def _is_last_day_of_month(date: Date) -> bool:
    """
    Indicates if the date is the last day of the month.
    """
    return date.day == calendar.monthrange(date.year, date.month)[1]


def _last_payment_date(start: Date, asof: Date, frequency: Union[int, Decimal], eom: Optional[int] = None) -> Date:
    """
    Returns the last coupon payment date.

    >>> _last_payment_date(datetime.date(2014,  1,  1), datetime.date(2015, 12, 31), 1)
    datetime.date(2015, 1, 1)

    >>> _last_payment_date(datetime.date(2015,  1,  1), datetime.date(2015, 12, 31), 1)
    datetime.date(2015, 1, 1)

    >>> _last_payment_date(datetime.date(2014,  1,  1), datetime.date(2015, 12, 31), 2)
    datetime.date(2015, 7, 1)

    >>> _last_payment_date(datetime.date(2014,  1,  1), datetime.date(2015,  8, 31), 2)
    datetime.date(2015, 7, 1)

    >>> _last_payment_date(datetime.date(2014,  1,  1), datetime.date(2015,  4, 30), 2)
    datetime.date(2015, 1, 1)

    >>> _last_payment_date(datetime.date(2014,  6,  1), datetime.date(2015,  4, 30), 1)
    datetime.date(2014, 6, 1)

    >>> _last_payment_date(datetime.date(2008,  7,  7), datetime.date(2015, 10,  6), 4)
    datetime.date(2015, 7, 7)

    >>> _last_payment_date(datetime.date(2014, 12,  9), datetime.date(2015, 12,  4), 1)
    datetime.date(2014, 12, 9)

    >>> _last_payment_date(datetime.date(2012, 12, 15), datetime.date(2016,  1,  6), 2)
    datetime.date(2015, 12, 15)

    >>> _last_payment_date(datetime.date(2012, 12, 15), datetime.date(2015, 12, 31), 2)
    datetime.date(2015, 12, 15)
    """
    ## Make sure that we have eom:
    eom = eom or start.day

    ## Get the starting month:
    s_month = start.month

    ## Get the period:
    period = int(12 / frequency)

    ## Get the current day, month and year:
    c_day, c_month, c_year = asof.day, asof.month, asof.year

    ## Get the payment schedule:
    schedule = sorted([i > 0 and i or 12 for i in sorted([(i + s_month) % 12 for i in range(0, 12, period)])])

    ## Filter out previous:
    future = [month for month in schedule if (month < c_month) or (month == c_month and eom <= c_day)]

    ## Get the previous month and year:
    p_year, p_month = (c_year, future[-1]) if future else (c_year - 1, schedule[-1])

    ## Return the date:
    if p_year < 1 or p_month < 1 or eom < 1:
        return start

    ## Construct and return the date safely:
    return _construct_date(p_year, p_month, eom)


def _next_payment_date(start: Date, frequency: Union[int, Decimal], eom: Optional[int] = None) -> Date:
    """
    Returns the last coupon payment date.

    >>> _next_payment_date(datetime.date(2014,  1,  1), 1, None)
    datetime.date(2015, 1, 1)

    >>> _next_payment_date(datetime.date(2014,  1,  1), 1, 15)
    datetime.date(2015, 1, 15)
    """
    ## Get the number of months to move forward:
    months = int(12 / frequency)

    ## Find the next date:
    nextdate = start + relativedelta(months=months)

    ## Do we have any end of month?
    if eom:
        try:
            nextdate = nextdate.replace(day=eom)
        except ValueError:
            pass

    ## Done, return:
    return nextdate


def _construct_date(year: int, month: int, day: int) -> Date:
    """
    Constructs and returns date safely.
    """
    if year <= 0 or month <= 0 or day <= 0:
        raise ValueError("year, month and day must be greater than 0.")
    try:
        return datetime.date(year, month, day)
    except ValueError as exc:
        if str(exc) == "day is out of range for month":
            return _construct_date(year, month, day - 1)
        else:
            raise exc


class DCC(NamedTuple):
    """
    Defines a day count convention model.
    """

    #: Defines the name of the day count convention.
    name: str

    #: Defines a set of alternative names of the day count convention.
    altnames: Set[str]

    #: Defines a set of currencies which are known to use this convention by default.
    currencies: Set[Currency]

    #: Defines the day count fraction calculation method function.
    calculate_fraction_method: DCFC

    def calculate_fraction(self, start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
        """
        Calculates the day count fraction based on the underlying methodology after performing some general checks.
        """
        ## Checks if dates are provided properly:
        if not start <= asof <= end:
            ## Nope, return 0:
            return ZERO

        ## Cool, we can proceed with calculation based on the methodology:
        return self[3](start, asof, end, freq)

    def calculate_daily_fraction(self, start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
        """
        Calculates daily fraction.
        """
        ## Get t-1 for asof:
        asof_minus_1 = asof - datetime.timedelta(days=1)

        ## Get the yesterday's factor:
        if asof_minus_1 < start:
            yfact = ZERO
        else:
            yfact = self.calculate_fraction_method(start, asof_minus_1, end, freq)

        ## Get today's factor:
        tfact = self.calculate_fraction_method(start, asof, end, freq)

        ## Get the factor and return:
        return tfact - yfact

    def interest(
        self,
        principal: Money,
        rate: Decimal,
        start: Date,
        asof: Date,
        end: Optional[Date] = None,
        freq: Optional[Decimal] = None,
    ) -> Money:
        """
        Calculates the accrued interest.
        """
        return principal * rate * self.calculate_fraction(start, asof, end or asof, freq)

    def coupon(
        self,
        principal: Money,
        rate: Decimal,
        start: Date,
        asof: Date,
        end: Date,
        freq: Union[int, Decimal],
        eom: Optional[int] = None,
    ) -> Money:
        """
        Calculates the accrued interest for the coupon payment.

        This method is primarily used for bond coupon accruals which assumes the start date to be the first of regular
        payment schedules.
        """
        ## Find the previous and next payment dates:
        prevdate = _last_payment_date(start, asof, freq, eom)
        nextdate = _next_payment_date(prevdate, freq, eom)

        ## Calculate the interest and return:
        return self.interest(principal, rate, prevdate, asof, nextdate, Decimal(freq))


class DCCRegistryMachinery:
    """
    Provides the day count registry model.

    >>> principal = Money.of(Currencies["USD"], Decimal(1000000), datetime.date.today())
    >>> start = datetime.date(2007, 12, 28)
    >>> end = datetime.date(2008, 2, 28)
    >>> rate = Decimal(0.01)
    >>> dcc = DCCRegistry.find("Act/Act")
    >>> round(dcc.calculate_fraction(start, end, end), 14)
    Decimal('0.16942884946478')
    >>> dcc.interest(principal, rate, start, end, end).qty
    Decimal('1694.29')
    >>> dcc.interest(principal, rate, end, start, start).qty
    Decimal('0.00')
    """

    def __init__(self) -> None:
        """
        Initializes the registry.
        """
        ## Define the main registry buffer:
        self._buffer_main: Dict[str, DCC] = {}

        ## Defines the registry buffer for alternative DCC names:
        self._buffer_altn: Dict[str, DCC] = {}

    def _is_registered(self, name: str) -> bool:
        """
        Checks if the given name is ever registered before.
        """
        return name in self._buffer_main or name in self._buffer_altn

    def register(self, dcc: DCC) -> None:
        """
        Attempts to register the given day count convention.
        """
        ## Check if the main name is ever registered before:
        if self._is_registered(dcc.name):
            ## Yep, raise a TypeError:
            raise TypeError(f"Day count convention '{dcc.name}' is already registered")

        ## Add to the main buffer:
        self._buffer_main[dcc.name] = dcc

        ## Check if there is any registry conflict:
        for name in dcc.altnames:
            ## Check if the name is ever registered:
            if self._is_registered(name):
                ## Yep, raise a TypeError:
                raise TypeError(f"Day count convention '{dcc.name}' is already registered")

            ## Register to the alternative buffer:
            self._buffer_altn[name] = dcc

    def _find_strict(self, name: str) -> Optional[DCC]:
        """
        Attempts to find the day count convention by the given name.
        """
        return self._buffer_main.get(name) or self._buffer_altn.get(name)

    def find(self, name: str) -> Optional[DCC]:
        """
        Attempts to find the day count convention by the given name.

        Note that all day count conventions are registered under stripped, uppercased names. Therefore,
        the implementation will first attempt to find by given name as is. If it can not find it, it will
        strip and uppercase the name and try to find it as such as a last resort.
        """
        return self._find_strict(name) or self._find_strict(name.strip().upper())

    @property
    def registry(self) -> List[DCC]:
        """
        Returns the main registry values.
        """
        return list(self._buffer_main.values())

    @property
    def table(self) -> Dict[str, DCC]:
        """
        Returns a lookup table for available day count conventions.
        """
        return {**{k: v for k, v in self._buffer_main.items()}, **{k: v for k, v in self._buffer_altn.items()}}


#: Defines the default DCC registry.
DCCRegistry = DCCRegistryMachinery()


def dcc(name: str, altnames: Optional[Set[str]] = None, ccys: Optional[Set[Currency]] = None) -> Callable[[DCFC], DCFC]:
    """
    Registers a day count fraction calculator under the given names and alternative names (if any).

    :param name: The name of the day count convention.
    :param altnames: A set of alternative names of the day count convention, if any.
    :param ccys: A set of currencies which are known to use this convention by default, if any.
    :return: Registered day count fraction calculation function.
    """

    def register_and_return_dcfc(func: DCFC) -> DCFC:
        """
        Registers the given day count fraction calculator and returns it.

        :param func: Day count fraction calculation function to be registered.
        :return: Registered day count fraction calculation function.
        """
        ## Create the DCC instance:
        dcc = DCC(name, altnames or set([]), ccys or set([]), func)

        ## Attempt to register the DCC:
        DCCRegistry.register(dcc)

        ## Attach the dcc instance to the day count fraction calculation function (for whatever it is worth):
        setattr(func, "__dcc", dcc)

        ## Done, return the function (if above statment did not raise any exceptions):
        return func

    return register_and_return_dcfc


@dcc("Act/Act", {"Actual/Actual", "Actual/Actual (ISDA)"})
def dcfc_act_act(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for "Act/Act" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :param freq: The frequency of payments in a year.
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_act(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16942884946478')
    >>> round(dcfc_act_act(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17216108990194')
    >>> round(dcfc_act_act(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08243131970956')
    >>> round(dcfc_act_act(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32625945055768')
    """
    ## Get all years of interest by checking the leap year:
    years = {year: calendar.isleap(year) for year in range(start.year, asof.year + 1)}

    ## Define the buffer of days for the day count. The former is for non-leap years, the latter for leap years:
    buffer: List[int] = [0, 0]

    ## Iterate over the date range and count:
    for date in _get_date_range(start, asof):
        ## Check the year and modify buffer accordingly:
        if years[date.year]:
            ## Yep, it is a leap year:
            buffer[1] += 1
        else:
            ## Nope, not a leap year:
            buffer[0] += 1

    ## Done, compute and return:
    return Decimal(buffer[0]) / Decimal(365) + Decimal(buffer[1]) / Decimal(366)


@dcc("Act/Act (ICMA)", {"Actual/Actual (ICMA)", "ISMA-99", "Act/Act (ISMA)"})
def dcfc_act_act_icma(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for "Act/Act (ICMA)" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof, ex1_end = datetime.date(2019, 3, 2), datetime.date(2019, 9, 10), datetime.date(2020, 3, 2)
    >>> round(dcfc_act_act_icma(start=ex1_start, asof=ex1_asof, end=ex1_end), 10)
    Decimal('0.5245901639')
    """
    ## Get the number of actual days:
    p1 = Decimal(_get_actual_day_count(start, asof))

    ## Get the number of days in the period:
    p2 = Decimal(_get_actual_day_count(start, end))

    ## Compute the ratio and return:
    return p1 / p2 / Decimal(freq or ONE)


@dcc(
    "Act/360",
    {"Actual/360", "French", "360"},
    _as_ccys({"AUD", "CAD", "CHF", "EUR", "USD", "DKK", "CZK", "HUF", "SEK", "IDR", "NOK", "JPY", "NZD", "THB"}),
)
def dcfc_act_360(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for "Act/360" convention.

    :param start: The start date of the period.
    :param end: The end date of the period.
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_360(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.17222222222222')
    >>> round(dcfc_act_360(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17500000000000')
    >>> round(dcfc_act_360(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.10000000000000')
    >>> round(dcfc_act_360(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.34722222222222')
    """
    return _get_actual_day_count(start, asof) / Decimal(360)


@dcc("Act/365F", {"Actual/365 Fixed", "English", "365"}, _as_ccys({"GBP", "HKD", "INR", "PLN", "SGD", "ZAR", "MYR"}))
def dcfc_act_365_f(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "Act/365F" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_365_f(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_act_365_f(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17260273972603')
    >>> round(dcfc_act_365_f(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08493150684932')
    >>> round(dcfc_act_365_f(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32876712328767')
    """
    return _get_actual_day_count(start, asof) / Decimal(365)


@dcc("Act/365A", {"Actual/365 Actual"})
def dcfc_act_365_a(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "Act/365A" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_365_a(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_act_365_a(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17213114754098')
    >>> round(dcfc_act_365_a(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08196721311475')
    >>> round(dcfc_act_365_a(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32513661202186')
    """
    return _get_actual_day_count(start, asof) / Decimal(366 if _has_leap_day(start, asof) else 365)


@dcc("Act/365L", {"Actual/365 Leap Year"})
def dcfc_act_365_l(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "Act/365L" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_365_l(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16939890710383')
    >>> round(dcfc_act_365_l(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17213114754098')
    >>> round(dcfc_act_365_l(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08196721311475')
    >>> round(dcfc_act_365_l(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32876712328767')
    """
    return _get_actual_day_count(start, asof) / Decimal(366 if calendar.isleap(asof.year) else 365)


@dcc("NL/365", {"Actual/365 No Leap Year", "NL365"})
def dcfc_nl_365(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "NL/365" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_nl_365(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_nl_365(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_nl_365(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08219178082192')
    >>> round(dcfc_nl_365(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32602739726027')
    """
    return (_get_actual_day_count(start, asof) - (1 if _has_leap_day(start, asof) else 0)) / Decimal(365)


@dcc("30/360 ISDA", {"30/360 US Municipal", "Bond Basis"})
def dcfc_30_360_isda(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "30/360 ISDA" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_360_isda(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_360_isda(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_360_isda(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_360_isda(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33333333333333')
    """
    ## Get the new start date, if required:
    if start.day == 31:
        start = datetime.date(start.year, start.month, 30)

    ## Get the new asof date, if required:
    if start.day == 30 and asof.day == 31:
        asof = datetime.date(asof.year, asof.month, 30)

    ## Compute number of days:
    nod = (asof.day - start.day) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30E/360", {"30/360 ISMA", "30/360 European", "30S/360 Special German", "Eurobond Basis"})
def dcfc_30_e_360(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "30E/360" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_e_360(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_e_360(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_e_360(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_e_360(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33055555555556')
    """
    ## Get the new start date, if required:
    if start.day == 31:
        start = datetime.date(start.year, start.month, 30)

    ## Get the new asof date, if required:
    if asof.day == 31:
        asof = datetime.date(asof.year, asof.month, 30)

    ## Compute number of days:
    nod = (asof.day - start.day) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30E+/360")
def dcfc_30_e_plus_360(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "30E+/360" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.


    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_e_plus_360(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_e_plus_360(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_e_plus_360(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_e_plus_360(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33333333333333')
    """
    ## Get the new start date, if required:
    if start.day == 31:
        start = datetime.date(start.year, start.month, 30)

    ## Get the new asof date, if required:
    if asof.day == 31:
        asof = asof + datetime.timedelta(days=1)

    ## Compute number of days:
    nod = (asof.day - start.day) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30/360 German", {"30E/360 ISDA"})
def dcfc_30_360_german(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_360_german(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_360_german(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_360_german(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_360_german(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33055555555556')
    """
    ## Get the new start date, if required:
    if start.day == 31 or (start.month == 2 and _is_last_day_of_month(start)):
        d1 = 30
    else:
        d1 = start.day

    ## Get the new asof date, if required:
    if asof.day == 31 or (asof.month == 2 and _is_last_day_of_month(asof) and end != asof):
        d2 = 30
    else:
        d2 = asof.day

    ## Compute number of days:
    nod = (d2 - d1) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30/360 US", {"30U/360", "30US/360"})
def dcfc_30_360_us(start: Date, asof: Date, end: Date, freq: Optional[Decimal] = None) -> Decimal:
    """
    Computes the day count fraction for the "30/360 US" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_360_us(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_360_us(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_360_us(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_360_us(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33333333333333')
    """
    ## Get D1 and D2:
    d1 = start.day
    d2 = asof.day

    ## Need to change D1?
    if _is_last_day_of_month(start):
        ## Yep, change it:
        d1 = 30

        ## Shall we change the d2, too?
        if _is_last_day_of_month(asof):
            d2 = 30

    ## Revisit d2:
    if d2 == 31 and (d1 == 30 or d1 == 31):
        d2 = 30

    ## Revisit d1:
    if d1 == 31:
        d1 = 30

    ## Compute number of days:
    nod = (d2 - d1) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, return:
    return nod / Decimal(360)
