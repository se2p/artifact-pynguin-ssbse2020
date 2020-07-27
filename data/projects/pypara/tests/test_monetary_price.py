import datetime
from decimal import Decimal

import pytest  # type: ignore

from pypara.currencies import Currencies
from pypara.monetary import IncompatibleCurrencyError, Money, NonePrice, NoPrice, Price, SomePrice

## Define some currencies:
eur = Currencies["EUR"]
usd = Currencies["USD"]

## Defines some Decimal quantities:
zero = Decimal("0")
half = Decimal("0.5")
one = Decimal("1")
two = Decimal("2")

## Define some dates:
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)


def test_implementation() -> None:
    ## Define instances:
    _price = Price()  # type: ignore
    sprice = SomePrice(usd, one, today)
    nprice = NonePrice()

    ## Check structure:
    assert _price.__slots__ == ()
    assert sprice.__slots__ == ()
    assert nprice.__slots__ == ()
    assert not hasattr(_price, "__dict__")
    assert not hasattr(sprice, "__dict__")
    assert not hasattr(nprice, "__dict__")

    ## Check types
    assert isinstance(Price.NA, Price)
    assert isinstance(Price.NA, NonePrice)
    assert not isinstance(Price.NA, SomePrice)
    assert not isinstance(Price.NA, Money)

    assert isinstance(_price, Price)
    assert not isinstance(_price, SomePrice)
    assert not isinstance(_price, NonePrice)

    assert isinstance(sprice, Price)
    assert isinstance(sprice, SomePrice)
    assert not isinstance(sprice, NonePrice)

    assert isinstance(nprice, Price)
    assert not isinstance(nprice, SomePrice)
    assert isinstance(nprice, NonePrice)


def test_of() -> None:
    assert Price.of(usd, one, None) == Price.NA
    assert Price.of(usd, None, today) == Price.NA
    assert Price.of(usd, one, None) == Price.NA
    assert Price.of(usd, one, today) == SomePrice(usd, one, today)


def test_is_equal() -> None:
    ## Vanilla:
    assert Price.NA.is_equal(NoPrice)
    assert Price.NA.is_equal(NonePrice())
    assert not Price.NA.is_equal(Price.of(usd, zero, today))
    assert Price.of(usd, zero, today).is_equal(Price.of(usd, zero, today))
    assert Price.of(usd, half, today).is_equal(Price.of(usd, half, today))
    assert not Price.of(usd, zero, today).is_equal(Price.of(eur, zero, today))
    assert not Price.of(usd, zero, today).is_equal(Price.of(usd, half, today))
    assert not Price.of(usd, zero, today).is_equal(Price.of(usd, zero, yesterday))

    ## With operator overload:
    assert Price.NA == NonePrice()
    assert Price.NA != Price.of(usd, zero, today)
    assert Price.of(usd, zero, today) == Price.of(usd, zero, today)
    assert Price.of(usd, half, today) == Price.of(usd, half, today)
    assert Price.of(usd, zero, today) != Price.of(eur, zero, today)
    assert Price.of(usd, zero, today) != Price.of(usd, half, today)
    assert Price.of(usd, zero, today) != Price.of(usd, zero, yesterday)


def test_to_boolean() -> None:
    ## Vanilla:
    assert not Price.NA.as_boolean()
    assert not Price.of(usd, zero, today).as_boolean()
    assert Price.of(usd, half, today).as_boolean()
    assert Price.of(usd, -half, today).as_boolean()

    ## With semantic overload
    assert not bool(Price.NA)
    assert not Price.of(usd, zero, today)
    assert Price.of(usd, half, today)
    assert Price.of(usd, -half, today)


def test_to_float() -> None:
    ## Vanilla:
    with pytest.raises(TypeError):
        Price.NA.as_float()
    assert Price.of(usd, half, today).as_float() == 0.5
    assert type(Price.of(usd, half, today).as_float()) == float

    ## With overload:
    with pytest.raises(TypeError):
        float(Price.NA)
    assert float(Price.of(usd, half, today)) == 0.5
    assert type(float(Price.of(usd, half, today))) == float


def test_to_integer() -> None:
    ## Vanilla:
    with pytest.raises(TypeError):
        int(Price.NA)
    assert int(Price.of(usd, half, today)) == 0
    assert type(int(Price.of(usd, half, today))) == int

    ## With overload:
    with pytest.raises(TypeError):
        Price.NA.as_integer()
    assert Price.of(usd, half, today).as_integer() == 0
    assert type(Price.of(usd, half, today).as_integer()) == int


def test_abs() -> None:
    ## Vanilla:
    assert Price.NA.abs() == Price.NA
    assert Price.of(usd, zero, today).abs() == Price.of(usd, zero, today)
    assert Price.of(usd, -one, today).abs() == Price.of(usd, +one, today)
    assert Price.of(usd, +one, today).abs() == Price.of(usd, +one, today)

    ## With overload:
    assert abs(Price.NA) == Price.NA
    assert abs(Price.of(usd, zero, today)) == Price.of(usd, zero, today)
    assert abs(Price.of(usd, -one, today)) == Price.of(usd, +one, today)
    assert abs(Price.of(usd, +one, today)) == Price.of(usd, +one, today)


def test_negative() -> None:
    ## Vanilla:
    assert Price.NA.negative() == Price.NA
    assert Price.of(usd, zero, today).negative() == Price.of(usd, zero, today)
    assert Price.of(usd, -one, today).negative() == Price.of(usd, +one, today)
    assert Price.of(usd, +one, today).negative() == Price.of(usd, -one, today)

    ## With overload:
    assert -Price.NA == Price.NA
    assert -Price.of(usd, zero, today) == Price.of(usd, zero, today)
    assert -Price.of(usd, -one, today) == Price.of(usd, +one, today)
    assert -Price.of(usd, +one, today) == Price.of(usd, -one, today)


def test_positive() -> None:
    ## Vanilla:
    assert Price.NA.positive() == Price.NA
    assert Price.of(usd, zero, today).positive() == Price.of(usd, zero, today)
    assert Price.of(usd, -one, today).positive() == Price.of(usd, -one, today)
    assert Price.of(usd, +one, today).positive() == Price.of(usd, +one, today)

    ## With overload:
    assert +Price.NA == Price.NA
    assert +Price.of(usd, zero, today) == Price.of(usd, zero, today)
    assert +Price.of(usd, -one, today) == Price.of(usd, -one, today)
    assert +Price.of(usd, +one, today) == Price.of(usd, +one, today)


def test_round() -> None:
    ## Vanilla:
    assert Price.NA.round(2) == Price.NA
    assert Price.of(usd, zero, today).round(2) == Price.of(usd, zero, today)
    assert Price.of(usd, -one, today).round(2) == Price.of(usd, -one, today)
    assert Price.of(usd, +one, today).round(2) == Price.of(usd, +one, today)

    ## Quick tests:
    assert Price.of(usd, Decimal("1.555"), today).round(2) == Price.of(usd, Decimal("1.56"), today)
    assert Price.of(usd, Decimal("1.545"), today).round(2) == Price.of(usd, Decimal("1.54"), today)

    ## With overload:
    assert round(Price.NA, 2) == Price.NA
    assert round(Price.of(usd, zero, today), 2) == Price.of(usd, zero, today)
    assert round(Price.of(usd, -one, today), 2) == Price.of(usd, -one, today)
    assert round(Price.of(usd, +one, today), 2) == Price.of(usd, +one, today)
    assert round(Price.of(usd, Decimal("1.555"), today), 2) == Price.of(usd, Decimal("1.56"), today)
    assert round(Price.of(usd, Decimal("1.545"), today), 2) == Price.of(usd, Decimal("1.54"), today)

    ## TODO: Following two are not really what round function signature says. mypy can't detect it!
    assert round(Price.of(usd, Decimal("1.4"), today)) == Price.of(usd, Decimal("1"), today)
    assert round(Price.of(usd, Decimal("1.5"), today)) == Price.of(usd, Decimal("2"), today)


def test_addition() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.add(Price.NA) == Price.NA
    assert Price.NA.add(Price.of(usd, zero, today)) == Price.of(usd, zero, today)
    assert Price.of(usd, zero, today).add(Price.NA) == Price.of(usd, zero, today)

    ## Vanilla addition:
    assert Price.of(usd, zero, today).add(Price.of(usd, zero, today)) == Price.of(usd, zero, today)
    assert Price.of(usd, zero, today).add(Price.of(usd, one, today)) == Price.of(usd, one, today)
    assert Price.of(usd, one, today).add(Price.of(usd, one, today)) == Price.of(usd, two, today)
    assert Price.of(usd, one, today).add(Price.of(usd, -one, today)) == Price.of(usd, zero, today)

    ## Carry dates forward:
    assert Price.of(usd, zero, today).add(Price.of(usd, one, yesterday)) == Price.of(usd, one, today)
    assert Price.of(usd, zero, yesterday).add(Price.of(usd, one, today)) == Price.of(usd, one, today)

    ## Incompatible currency errors:
    with pytest.raises(IncompatibleCurrencyError):
        Price.of(usd, zero, today).add(Price.of(eur, zero, today))

    ## Operator overload:
    assert Price.NA + Price.NA == Price.NA
    assert Price.NA + Price.of(usd, zero, today) == Price.of(usd, zero, today)
    assert Price.of(usd, zero, today) + Price.NA == Price.of(usd, zero, today)
    assert Price.of(usd, zero, today) + Price.of(usd, one, today) == Price.of(usd, one, today)


def test_scalar_addition() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.scalar_add(1) == Price.NA

    ## Vanilla addition:
    assert Price.of(usd, zero, today).scalar_add(1) == Price.of(usd, one, today)
    assert Price.of(usd, zero, today).scalar_add(1.0) == Price.of(usd, one, today)
    assert Price.of(usd, zero, today).scalar_add(one) == Price.of(usd, one, today)
    assert Price.of(usd, zero, today).scalar_add(-1) == Price.of(usd, -one, today)


def test_subtraction() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.subtract(Price.NA) == Price.NA
    assert Price.NA.subtract(Price.of(usd, zero, today)) == Price.of(usd, zero, today)
    assert Price.of(usd, zero, today).subtract(Price.NA) == Price.of(usd, zero, today)

    ## Vanilla subtraction:
    assert Price.of(usd, zero, today).subtract(Price.of(usd, zero, today)) == Price.of(usd, zero, today)
    assert Price.of(usd, zero, today).subtract(Price.of(usd, one, today)) == Price.of(usd, -one, today)
    assert Price.of(usd, one, today).subtract(Price.of(usd, one, today)) == Price.of(usd, zero, today)
    assert Price.of(usd, one, today).subtract(Price.of(usd, -one, today)) == Price.of(usd, two, today)

    ## Carry dates forward:
    assert Price.of(usd, zero, today).subtract(Price.of(usd, one, yesterday)) == Price.of(usd, -one, today)
    assert Price.of(usd, zero, yesterday).subtract(Price.of(usd, one, today)) == Price.of(usd, -one, today)

    ## Incompatible currency errors:
    with pytest.raises(IncompatibleCurrencyError):
        Price.of(usd, zero, today).subtract(Price.of(eur, zero, today))

    ## Operator overload:
    assert Price.of(usd, zero, today) - Price.of(usd, one, today) == Price.of(usd, -one, today)
    assert Price.NA - Price.NA == Price.NA
    assert Price.NA - Price.of(usd, zero, today) == Price.of(usd, zero, today)
    assert Price.of(usd, zero, today) - Price.NA == Price.of(usd, zero, today)


def test_scalar_subtraction() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.scalar_subtract(1) == Price.NA

    ## Vanilla subtraction:
    assert Price.of(usd, zero, today).scalar_subtract(1) == Price.of(usd, -one, today)
    assert Price.of(usd, zero, today).scalar_subtract(1.0) == Price.of(usd, -one, today)
    assert Price.of(usd, zero, today).scalar_subtract(one) == Price.of(usd, -one, today)
    assert Price.of(usd, zero, today).scalar_subtract(-1) == Price.of(usd, one, today)

    ## Operator overload:
    assert Price.of(usd, zero, today).scalar_subtract(1) == Price.of(usd, -one, today)
    assert Price.of(usd, zero, today).scalar_subtract(-1) == Price.of(usd, one, today)


def test_scalar_multiplication() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.multiply(1) == Price.NA

    ## Vanilla subtraction:
    assert Price.of(usd, one, today).multiply(1) == Price.of(usd, one, today)
    assert Price.of(usd, one, today).multiply(2) == Price.of(usd, two, today)
    assert Price.of(usd, -one, today).multiply(1) == Price.of(usd, -one, today)
    assert Price.of(usd, -one, today).multiply(2) == Price.of(usd, -two, today)

    ## Other types:
    assert Price.of(usd, one, today).multiply(1) == Price.of(usd, one, today)
    assert Price.of(usd, one, today).multiply(1.0) == Price.of(usd, one, today)
    assert Price.of(usd, one, today).multiply(one) == Price.of(usd, one, today)

    ## Operator overload:
    assert Price.NA * 1 == Price.NA
    assert Price.of(usd, one, today) * 1 == Price.of(usd, one, today)
    assert Price.of(usd, one, today) * 2 == Price.of(usd, two, today)
    assert Price.of(usd, -one, today) * 1 == Price.of(usd, -one, today)
    assert Price.of(usd, -one, today) * 2 == Price.of(usd, -two, today)


def test_monetary_multiplication() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.times(1) == Money.NA

    ## Vanilla multiplication:
    assert Price.of(usd, one, today).times(1) == Money.of(usd, one, today)
    assert Price.of(usd, one, today).times(2) == Money.of(usd, two, today)
    assert Price.of(usd, -one, today).times(1) == Money.of(usd, -one, today)
    assert Price.of(usd, -one, today).times(2) == Money.of(usd, -two, today)

    ## Other types:
    assert Price.of(usd, one, today).times(1) == Money.of(usd, one, today)
    assert Price.of(usd, one, today).times(1.0) == Money.of(usd, one, today)
    assert Price.of(usd, one, today).times(one) == Money.of(usd, one, today)


def test_division() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.divide(1) == Price.NA

    ## Vanilla subtraction:
    assert Price.of(usd, one, today).divide(1) == Price.of(usd, one, today)
    assert Price.of(usd, one, today).divide(2) == Price.of(usd, half, today)
    assert Price.of(usd, -one, today).divide(1) == Price.of(usd, -one, today)
    assert Price.of(usd, -one, today).divide(2) == Price.of(usd, -half, today)

    ## Various divisor types:
    assert Price.of(usd, one, today).divide(2) == Price.of(usd, half, today)
    assert Price.of(usd, one, today).divide(2.0) == Price.of(usd, half, today)
    assert Price.of(usd, one, today).divide(two) == Price.of(usd, half, today)

    ## Division by zero:
    assert Price.of(usd, one, today).divide(0) == Price.NA
    assert Price.of(usd, one, today).divide(zero) == Price.NA
    assert Price.of(usd, one, today).divide(0.0) == Price.NA

    ## Operator overload:
    assert Price.NA / 1 == Price.NA
    assert Price.of(usd, one, today) / 1 == Price.of(usd, one, today)
    assert Price.of(usd, one, today) / 2 == Price.of(usd, half, today)
    assert Price.of(usd, -one, today) / 1 == Price.of(usd, -one, today)
    assert Price.of(usd, -one, today) / 2 == Price.of(usd, -half, today)
    assert Price.of(usd, -one, today) / 0 == Price.NA


def test_floor_division() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.floor_divide(1) == Price.NA

    ## Vanilla subtraction:
    assert Price.of(usd, one, today).floor_divide(1) == Price.of(usd, one, today)
    assert Price.of(usd, one, today).floor_divide(2) == Price.of(usd, zero, today)
    assert Price.of(usd, -one, today).floor_divide(1) == Price.of(usd, -one, today)
    assert Price.of(usd, -one, today).floor_divide(2) == Price.of(usd, zero, today)

    ## Various divisor types:
    assert Price.of(usd, one, today).floor_divide(2) == Price.of(usd, zero, today)
    assert Price.of(usd, one, today).floor_divide(2.0) == Price.of(usd, zero, today)
    assert Price.of(usd, one, today).floor_divide(two) == Price.of(usd, zero, today)

    ## Division by zero:
    assert Price.of(usd, one, today).floor_divide(0) == Price.NA
    assert Price.of(usd, one, today).floor_divide(zero) == Price.NA
    assert Price.of(usd, one, today).floor_divide(0.0) == Price.NA

    ## Operator overload:
    assert Price.NA / 1 == Price.NA
    assert Price.of(usd, one, today) // 1 == Price.of(usd, one, today)
    assert Price.of(usd, one, today) // 2 == Price.of(usd, zero, today)
    assert Price.of(usd, -one, today) // 1 == Price.of(usd, -one, today)
    assert Price.of(usd, -one, today) // 2 == Price.of(usd, zero, today)
    assert Price.of(usd, -one, today) // 0 == Price.NA


def test_comparisons() -> None:
    ## First use `Price.NA`s:
    assert not (Price.NA < Price.NA)
    assert Price.NA <= Price.NA
    assert not (Price.NA > Price.NA)
    assert Price.NA >= Price.NA

    ## Try mixed:
    assert Price.NA < Price.of(usd, -one, today)
    assert Price.NA <= Price.of(usd, -one, today)
    assert not (Price.NA > Price.of(usd, -one, today))
    assert not (Price.NA >= Price.of(usd, -one, today))

    ## ... and:
    assert not (Price.of(usd, -one, today) < Price.NA)
    assert not (Price.of(usd, -one, today) <= Price.NA)
    assert Price.of(usd, -one, today) > Price.NA
    assert Price.of(usd, -one, today) >= Price.NA

    ## With defined values:
    assert not (Price.of(usd, zero, today) < Price.of(usd, zero, today))
    assert Price.of(usd, zero, today) <= Price.of(usd, zero, today)
    assert not (Price.of(usd, zero, today) > Price.of(usd, zero, today))
    assert Price.of(usd, zero, today) >= Price.of(usd, zero, today)

    ## ... and:
    assert Price.of(usd, zero, today) < Price.of(usd, one, today)
    assert Price.of(usd, zero, today) <= Price.of(usd, one, today)
    assert not (Price.of(usd, zero, today) > Price.of(usd, one, today))
    assert not (Price.of(usd, zero, today) >= Price.of(usd, one, today))

    ## ... and:
    assert not (Price.of(usd, one, today) < Price.of(usd, zero, today))
    assert not (Price.of(usd, one, today) <= Price.of(usd, zero, today))
    assert Price.of(usd, one, today) > Price.of(usd, zero, today)
    assert Price.of(usd, one, today) >= Price.of(usd, zero, today)


def test_with() -> None:
    ## First use `Price.NA`s:
    assert Price.NA.with_ccy(usd) == Price.NA
    assert Price.NA.with_qty(one) == Price.NA
    assert Price.NA.with_dov(today) == Price.NA

    ## Now with some:
    assert Price.of(usd, zero, today).with_ccy(eur) == Price.of(eur, zero, today)
    assert Price.of(usd, zero, today).with_qty(one) == Price.of(usd, one, today)
    assert Price.of(usd, zero, today).with_dov(yesterday) == Price.of(usd, zero, yesterday)


def test_types() -> None:
    assert isinstance(Price.NA, Price)
    assert isinstance(Price.NA, NonePrice)
    assert not isinstance(Price.NA, SomePrice)
    assert not isinstance(Price.NA, Money)
