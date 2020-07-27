"""
This module provides currency definitions and related functionality.
"""

__all__ = ["Currencies", "Currency", "CurrencyLookupError", "CurrencyRegistry", "CurrencyType"]

from collections import OrderedDict
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .commons.errors import ProgrammingError
from .commons.numbers import ZERO, MaxPrecisionQuantizer, make_quantizer


class CurrencyLookupError(LookupError):
    """
    Provides a currency lookup error.
    """

    def __init__(self, code: str) -> None:
        """
        Initializes a currency lookup error.
        """
        ## Keep the code:
        self.code = code

        ## Set the message:
        super().__init__(f"Currency identified by code '{code}' does not exist")


class CurrencyType(Enum):
    """
    Defines available currency types.
    """

    #: Defines money currency as in common legal tender.
    MONEY = "Money"

    #: Defines precious metals currency type.
    METAL = "Precious Metal"

    #: Defines crypto currency type.
    CRYPTO = "Crypto Currency"

    #: Defines alternative currency type.
    ALTERNATIVE = "Alernative"


@dataclass(frozen=True, order=True)
class Currency:
    """
    Defines currency value object model which is extending ISO 4217 to embrace other currency types.

    Note that you should not call :class:`Currency` constructor directly, but instead use the :method:`Currency.build`.
    :method:`Currency.build` is responsible of performing some checks before creating the currency.

    Try with USD:

    >>> USD = Currency.of("USD", "US Dollars", 2, CurrencyType.MONEY)
    >>> USD.quantize(Decimal("1.005"))
    Decimal('1.00')
    >>> USD.quantize(Decimal("1.015"))
    Decimal('1.02')

    Now, with JPY which has a different precision than USD:

    >>> JPY = Currency.of("JPY", "Japanese Yen", 0, CurrencyType.MONEY)
    >>> JPY.quantize(Decimal("0.5"))
    Decimal('0')
    >>> JPY.quantize(Decimal("1.5"))
    Decimal('2')

    And with a weird currency which has no fixed precision.

    >>> ZZZ = Currency.of("ZZZ", "Some weird currency", -1, CurrencyType.CRYPTO)
    >>> ZZZ.quantize(Decimal("1.0000000000005"))
    Decimal('1.000000000000')
    >>> ZZZ.quantize(Decimal("1.0000000000015"))
    Decimal('1.000000000002')

    Equalities:

    >>> usd1 = Currency.of("USD", "US Dollars", 2, CurrencyType.MONEY)
    >>> usd2 = Currency.of("USD", "US Dollars", 2, CurrencyType.MONEY)
    >>> usdx = Currency.of("USD", "UX Dollars", 2, CurrencyType.MONEY)
    >>> usd1 == usd2
    True
    >>> usd1 == usdx
    False
    >>> hash(usd1) == hash(usd2)
    True
    >>> hash(usd1) == hash(usdx)
    False
    """

    #: Defines the code of the currency.
    code: str

    #: Defines the name of the currency.
    name: str

    #: Defines the number of decimals of the currency.
    decimals: int

    #: Defines the type of the currency.
    type: CurrencyType

    #: Defines the quantiser of the currency.
    quantizer: Decimal

    #: Defines the pre-computed, cached hash.
    hashcache: int

    def __eq__(self, other: Any) -> bool:
        """
        Checks if the `self` and `other` are same currencies.
        """
        return isinstance(other, Currency) and self.hashcache == other.hashcache

    def __hash__(self) -> int:
        """
        Returns the pre-computed and cached hash.
        """
        return self.hashcache

    def quantize(self, qty: Decimal) -> Decimal:
        """
        Quantizes the decimal ``qty`` wrt to ccy's minor units fraction. Note that
        the [ROUND HALF TO EVEN](https://en.wikipedia.org/wiki/Rounding) method
        is used for rounding purposes.

        **Note** that the HALF-TO-EVEN method is inherited from the default decimal context instead of
        explicitly passing it. Therefore, if call-site application is making changes to the default
        context, the rounding method may not be HALF-TO-EVEN anymore.
        """
        return qty.quantize(self.quantizer)

    @classmethod
    def of(cls, code: str, name: str, decimals: int, ctype: CurrencyType) -> "Currency":
        """
        Attempts to create a currency instance and returns it.
        """
        ## Check the code:
        ProgrammingError.passert(isinstance(code, str), "Currency code must be a string")
        ProgrammingError.passert(code.isalpha(), "Currency code must contain only alphabetic characters")
        ProgrammingError.passert(code.isupper(), "Currency code must be all uppercase")

        ## Check the name:
        ProgrammingError.passert(isinstance(name, str), "Currency name must be a string")
        ProgrammingError.passert(name != "", "Currency name can not be empty")
        ProgrammingError.passert(not (name.startswith(" ") or name.endswith(" ")), "Trim the currency name")

        ## Check the decimals:
        ProgrammingError.passert(isinstance(decimals, int), "Number of decimals must be an integer")
        ProgrammingError.passert(decimals >= -1, "Number of decimals can not be less than -1")

        ## Check the type:
        ProgrammingError.passert(isinstance(ctype, CurrencyType), "Currency Type must be of type `CurrencyType`")

        ## Define the quantizer:
        if decimals > 0:
            quantizer = make_quantizer(decimals)
        elif decimals < 0:
            quantizer = MaxPrecisionQuantizer
        else:
            quantizer = ZERO

        ## By now, we should have all required instance attributes. However, we want to compute and cache the hash.
        hashcode = hash((code, name, decimals, ctype, quantizer))

        ## Done, create the currency object and return:
        return Currency(code, name, decimals, ctype, quantizer, hashcode)


class CurrencyRegistry:
    """
    Defines a currency registry model.

    >>> "USD" in Currencies
    True
    >>> Currencies.has("USD")
    True
    >>> "XXX" in Currencies
    False
    >>> Currencies.has("XXX")
    False
    >>> Currencies["USD"].code
    'USD'
    >>> Currencies["USD"].name
    'US Dollar'
    >>> Currencies["USD"].type.name
    'MONEY'
    >>> Currencies.get("USD") == Currencies["USD"]
    True
    >>> Currencies.get("XXX")
    >>> Currencies.get("XXX", default=Currencies["USD"]) == Currencies["USD"]
    True
    >>> assert len(Currencies) == len(Currencies.all)
    >>> assert Currencies.codes == [currency.code for currency in Currencies.all]
    >>> assert Currencies.codenames == [(currency.code, currency.name) for currency in Currencies.all]
    """

    #: Defines the singleton instance.
    __instance = None  # type: CurrencyRegistry

    def __new__(cls) -> "CurrencyRegistry":
        """
        Creates the singleton instance, or returns the existing one.
        """
        ## Do we have the singleton instance?
        if CurrencyRegistry.__instance is None:
            ## Nope, not yet. Creat one:
            CurrencyRegistry.__instance = object.__new__(cls)

        ## Return the singleton instance.
        return CurrencyRegistry.__instance

    def __init__(self) -> None:
        """
        Initializes the currency registry.
        """
        ## Initialize the master registry container.
        self.__registry: Dict[str, Currency] = OrderedDict([])

        ## Initialize the currencies buffer.
        self.__currencies: List[Currency] = []

        ## Initialize the currency codes buffer.
        self.__codes: List[str] = []

        ## Initialize the code/name tuples buffer.
        self.__codenames: List[Tuple[str, str]] = []

        ## Define the registry population context open/close flag.
        self.__ctx_open: bool = False

    def __enter__(self) -> Callable[[Currency], None]:
        """
        Enters the registry population context.
        """
        ## Mark the context as open:
        self.__ctx_open = True

        ## OK, return the add method:
        return self.__register

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_value: Optional[str], tracebackx: Any) -> None:
        """
        Exits the registry population context and performs some finalization tasks.
        """
        ## Re-sort the registry:
        self.__registry = OrderedDict([(c.code, c) for c in sorted(self.__registry.values(), key=lambda x: x.code)])

        ## Re-sort currencies buffer:
        self.__currencies = [c for c in self.__registry.values()]

        ## Re-sort the currency codes buffer:
        self.__codes = [c.code for c in self.__currencies]

        ## Re-sort the choices buffer
        self.__codenames = [(c.code, c.name) for c in self.__currencies]

        ## Close the context:
        self.__ctx_open = False

    def __register(self, currency: Currency) -> None:
        """
        Attempts to add the currency to the registry.
        """
        ## Check of the registry population context is open:
        if not self.__ctx_open:
            ## Nope, raise error:
            raise ProgrammingError("Can not create currencies outside registry context.")

        ## Check if the currency is already added:
        if currency.code in self.__registry:
            raise ValueError(f"Currency {currency.code} is already registered.")

        ## Add to the containers:
        self.__registry[currency.code] = currency

    def __len__(self) -> int:
        """
        Returns the number of registered currencies.
        """
        return len(self.__registry)

    def __contains__(self, code: str) -> bool:
        """
        Checks if a given currency code is available.
        """
        return code in self.__registry

    def __getitem__(self, code: str) -> Currency:
        """
        Returns the currency identified by the code or raises lookup error.
        """
        try:
            return self.__registry[code]
        except KeyError:
            raise CurrencyLookupError(code)

    def has(self, code: str) -> bool:
        """
        Indicates if the code is a valid currency code.
        """
        return code in self.__registry

    def get(self, code: str, default: Optional[Currency] = None) -> Optional[Currency]:
        """
        Returns the currency for the given code.

        Note that if the code is not a valid currency code, a currency lookup error is raised.
        """
        return self.__registry.get(code, default)

    @property
    def all(self) -> List["Currency"]:
        """
        Returns the list of currencies.
        """
        return self.__currencies

    @property
    def codes(self) -> List[str]:
        """
        Returns a list of codes.
        """
        return self.__codes

    @property
    def codenames(self) -> List[Tuple[str, str]]:
        """
        Returns a list of code/name tuples.
        """
        return self.__codenames


#: Defines the global currencies registry.
Currencies = CurrencyRegistry()


## Create and register currencies in one go:
with Currencies as register:
    register(Currency.of("AED", "UAE Dirham", 2, CurrencyType.MONEY))
    register(Currency.of("AFN", "Afghani", 2, CurrencyType.MONEY))
    register(Currency.of("ALL", "Lek", 2, CurrencyType.MONEY))
    register(Currency.of("AMD", "Armenian Dram", 2, CurrencyType.MONEY))
    register(Currency.of("ANG", "Netherlands Antillean Guilder", 2, CurrencyType.MONEY))
    register(Currency.of("AOA", "Kwanza", 2, CurrencyType.MONEY))
    register(Currency.of("ARS", "Argentine Peso", 2, CurrencyType.MONEY))
    register(Currency.of("AUD", "Australian Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("AWG", "Aruban Florin", 2, CurrencyType.MONEY))
    register(Currency.of("AZN", "Azerbaijanian Manat", 2, CurrencyType.MONEY))
    register(Currency.of("BAM", "Convertible Mark", 2, CurrencyType.MONEY))
    register(Currency.of("BBD", "Barbados Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("BCH", "Bitcoin Cash", -1, CurrencyType.CRYPTO))
    register(Currency.of("BDT", "Taka", 2, CurrencyType.MONEY))
    register(Currency.of("BGN", "Bulgarian Lev", 2, CurrencyType.MONEY))
    register(Currency.of("BHD", "Bahraini Dinar", 3, CurrencyType.MONEY))
    register(Currency.of("BIF", "Burundi Franc", 0, CurrencyType.MONEY))
    register(Currency.of("BMD", "Bermudian Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("BND", "Brunei Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("BOB", "Boliviano", 2, CurrencyType.MONEY))
    register(Currency.of("BOV", "Mvdol", 2, CurrencyType.MONEY))
    register(Currency.of("BRL", "Brazilian Real", 2, CurrencyType.MONEY))
    register(Currency.of("BSD", "Bahamian Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("BTC", "Bitcoin", -1, CurrencyType.CRYPTO))
    register(Currency.of("BTN", "Ngultrum", 2, CurrencyType.MONEY))
    register(Currency.of("BWP", "Pula", 2, CurrencyType.MONEY))
    register(Currency.of("BYR", "Belarussian Ruble", 0, CurrencyType.MONEY))
    register(Currency.of("BZD", "Belize Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("CAD", "Canadian Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("CDF", "Congolese Franc", 2, CurrencyType.MONEY))
    register(Currency.of("CHE", "WIR Euro", 2, CurrencyType.MONEY))
    register(Currency.of("CHF", "Swiss Franc", 2, CurrencyType.MONEY))
    register(Currency.of("CHW", "WIR Franc", 2, CurrencyType.MONEY))
    register(Currency.of("CLF", "Unidad de Fomento", 4, CurrencyType.MONEY))
    register(Currency.of("CLP", "Chilean Peso", 0, CurrencyType.MONEY))
    register(Currency.of("CNH", "Yuan Renminbi (Off-shore)", 2, CurrencyType.MONEY))
    register(Currency.of("CNY", "Yuan Renminbi", 2, CurrencyType.MONEY))
    register(Currency.of("COP", "Colombian Peso", 2, CurrencyType.MONEY))
    register(Currency.of("COU", "Unidad de Valor Real", 2, CurrencyType.MONEY))
    register(Currency.of("CRC", "Costa Rican Colon", 2, CurrencyType.MONEY))
    register(Currency.of("CUC", "Peso Convertible", 2, CurrencyType.MONEY))
    register(Currency.of("CUP", "Cuban Peso", 2, CurrencyType.MONEY))
    register(Currency.of("CVE", "Cabo Verde Escudo", 2, CurrencyType.MONEY))
    register(Currency.of("CZK", "Czech Koruna", 2, CurrencyType.MONEY))
    register(Currency.of("DASH", "Dash", -1, CurrencyType.CRYPTO))
    register(Currency.of("DJF", "Djibouti Franc", 0, CurrencyType.MONEY))
    register(Currency.of("DKK", "Danish Krone", 2, CurrencyType.MONEY))
    register(Currency.of("DOP", "Dominican Peso", 2, CurrencyType.MONEY))
    register(Currency.of("DZD", "Algerian Dinar", 2, CurrencyType.MONEY))
    register(Currency.of("EGP", "Egyptian Pound", 2, CurrencyType.MONEY))
    register(Currency.of("EOS", "EOSIO", -1, CurrencyType.CRYPTO))
    register(Currency.of("ERN", "Nakfa", 2, CurrencyType.MONEY))
    register(Currency.of("ETB", "Ethiopian Birr", 2, CurrencyType.MONEY))
    register(Currency.of("ETC", "Ethereum Classic", -1, CurrencyType.CRYPTO))
    register(Currency.of("ETH", "Ethereum", -1, CurrencyType.CRYPTO))
    register(Currency.of("EUR", "Euro", 2, CurrencyType.MONEY))
    register(Currency.of("FJD", "Fiji Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("FKP", "Falkland Islands Pound", 2, CurrencyType.MONEY))
    register(Currency.of("GBP", "Pound Sterling", 2, CurrencyType.MONEY))
    register(Currency.of("GEL", "Lari", 2, CurrencyType.MONEY))
    register(Currency.of("GHS", "Ghana Cedi", 2, CurrencyType.MONEY))
    register(Currency.of("GIP", "Gibraltar Pound", 2, CurrencyType.MONEY))
    register(Currency.of("GMD", "Dalasi", 2, CurrencyType.MONEY))
    register(Currency.of("GNF", "Guinea Franc", 0, CurrencyType.MONEY))
    register(Currency.of("GTQ", "Quetzal", 2, CurrencyType.MONEY))
    register(Currency.of("GYD", "Guyana Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("HKD", "Hong Kong Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("HNL", "Lempira", 2, CurrencyType.MONEY))
    register(Currency.of("HRK", "Kuna", 2, CurrencyType.MONEY))
    register(Currency.of("HTG", "Gourde", 2, CurrencyType.MONEY))
    register(Currency.of("HUF", "Forint", 2, CurrencyType.MONEY))
    register(Currency.of("IDR", "Rupiah", 2, CurrencyType.MONEY))
    register(Currency.of("ILS", "New Israeli Sheqel", 2, CurrencyType.MONEY))
    register(Currency.of("INR", "Indian Rupee", 2, CurrencyType.MONEY))
    register(Currency.of("IOT", "IOTA", -1, CurrencyType.CRYPTO))
    register(Currency.of("IQD", "Iraqi Dinar", 3, CurrencyType.MONEY))
    register(Currency.of("IRR", "Iranian Rial", 2, CurrencyType.MONEY))
    register(Currency.of("ISK", "Iceland Krona", 0, CurrencyType.MONEY))
    register(Currency.of("JMD", "Jamaican Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("JOD", "Jordanian Dinar", 3, CurrencyType.MONEY))
    register(Currency.of("JPY", "Yen", 0, CurrencyType.MONEY))
    register(Currency.of("KES", "Kenyan Shilling", 2, CurrencyType.MONEY))
    register(Currency.of("KGS", "Som", 2, CurrencyType.MONEY))
    register(Currency.of("KHR", "Riel", 2, CurrencyType.MONEY))
    register(Currency.of("KMF", "Comoro Franc", 0, CurrencyType.MONEY))
    register(Currency.of("KPW", "North Korean Won", 2, CurrencyType.MONEY))
    register(Currency.of("KRW", "Won", 0, CurrencyType.MONEY))
    register(Currency.of("KWD", "Kuwaiti Dinar", 3, CurrencyType.MONEY))
    register(Currency.of("KYD", "Cayman Islands Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("KZT", "Tenge", 2, CurrencyType.MONEY))
    register(Currency.of("LAK", "Kip", 2, CurrencyType.MONEY))
    register(Currency.of("LBP", "Lebanese Pound", 2, CurrencyType.MONEY))
    register(Currency.of("LKR", "Sri Lanka Rupee", 2, CurrencyType.MONEY))
    register(Currency.of("LRD", "Liberian Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("LSL", "Loti", 2, CurrencyType.MONEY))
    register(Currency.of("LTC", "Litecoin", -1, CurrencyType.CRYPTO))
    register(Currency.of("LYD", "Libyan Dinar", 3, CurrencyType.MONEY))
    register(Currency.of("MAD", "Moroccan Dirham", 2, CurrencyType.MONEY))
    register(Currency.of("MDL", "Moldovan Leu", 2, CurrencyType.MONEY))
    register(Currency.of("MGA", "Malagasy Ariary", 2, CurrencyType.MONEY))
    register(Currency.of("MKD", "Denar", 2, CurrencyType.MONEY))
    register(Currency.of("MMK", "Kyat", 2, CurrencyType.MONEY))
    register(Currency.of("MNT", "Tugrik", 2, CurrencyType.MONEY))
    register(Currency.of("MOP", "Pataca", 2, CurrencyType.MONEY))
    register(Currency.of("MRO", "Ouguiya", 2, CurrencyType.MONEY))
    register(Currency.of("MUR", "Mauritius Rupee", 2, CurrencyType.MONEY))
    register(Currency.of("MVR", "Rufiyaa", 2, CurrencyType.MONEY))
    register(Currency.of("MWK", "Kwacha", 2, CurrencyType.MONEY))
    register(Currency.of("MXN", "Mexican Peso", 2, CurrencyType.MONEY))
    register(Currency.of("MXV", "Mexican Unidad de Inversion (UDI)", 2, CurrencyType.MONEY))
    register(Currency.of("MYR", "Malaysian Ringgit", 2, CurrencyType.MONEY))
    register(Currency.of("MZN", "Mozambique Metical", 2, CurrencyType.MONEY))
    register(Currency.of("NAD", "Namibia Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("NEO", "NEO", -1, CurrencyType.CRYPTO))
    register(Currency.of("NGN", "Naira", 2, CurrencyType.MONEY))
    register(Currency.of("NIO", "Cordoba Oro", 2, CurrencyType.MONEY))
    register(Currency.of("NOK", "Norwegian Krone", 2, CurrencyType.MONEY))
    register(Currency.of("NPR", "Nepalese Rupee", 2, CurrencyType.MONEY))
    register(Currency.of("NZD", "New Zealand Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("OMG", "OmiseGO", -1, CurrencyType.CRYPTO))
    register(Currency.of("OMR", "Rial Omani", 3, CurrencyType.MONEY))
    register(Currency.of("PAB", "Balboa", 2, CurrencyType.MONEY))
    register(Currency.of("PEN", "Nuevo Sol", 2, CurrencyType.MONEY))
    register(Currency.of("PGK", "Kina", 2, CurrencyType.MONEY))
    register(Currency.of("PHP", "Philippine Peso", 2, CurrencyType.MONEY))
    register(Currency.of("PKR", "Pakistan Rupee", 2, CurrencyType.MONEY))
    register(Currency.of("PLN", "Zloty", 2, CurrencyType.MONEY))
    register(Currency.of("PYG", "Guarani", 0, CurrencyType.MONEY))
    register(Currency.of("QAR", "Qatari Rial", 2, CurrencyType.MONEY))
    register(Currency.of("RON", "Romanian Leu", 2, CurrencyType.MONEY))
    register(Currency.of("RSD", "Serbian Dinar", 2, CurrencyType.MONEY))
    register(Currency.of("RUB", "Russian Ruble", 2, CurrencyType.MONEY))
    register(Currency.of("RWF", "Rwanda Franc", 0, CurrencyType.MONEY))
    register(Currency.of("SAR", "Saudi Riyal", 2, CurrencyType.MONEY))
    register(Currency.of("SBD", "Solomon Islands Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("SCR", "Seychelles Rupee", 2, CurrencyType.MONEY))
    register(Currency.of("SDG", "Sudanese Pound", 2, CurrencyType.MONEY))
    register(Currency.of("SEK", "Swedish Krona", 2, CurrencyType.MONEY))
    register(Currency.of("SGD", "Singapore Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("SHP", "Saint Helena Pound", 2, CurrencyType.MONEY))
    register(Currency.of("SLL", "Leone", 2, CurrencyType.MONEY))
    register(Currency.of("SOS", "Somali Shilling", 2, CurrencyType.MONEY))
    register(Currency.of("SRD", "Surinam Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("SSP", "South Sudanese Pound", 2, CurrencyType.MONEY))
    register(Currency.of("STD", "Dobra", 2, CurrencyType.MONEY))
    register(Currency.of("SVC", "El Salvador Colon", 2, CurrencyType.MONEY))
    register(Currency.of("SYP", "Syrian Pound", 2, CurrencyType.MONEY))
    register(Currency.of("SZL", "Lilangeni", 2, CurrencyType.MONEY))
    register(Currency.of("THB", "Baht", 2, CurrencyType.MONEY))
    register(Currency.of("TJS", "Somoni", 2, CurrencyType.MONEY))
    register(Currency.of("TMT", "Turkmenistan New Manat", 2, CurrencyType.MONEY))
    register(Currency.of("TND", "Tunisian Dinar", 3, CurrencyType.MONEY))
    register(Currency.of("TOP", "Pa'anga", 2, CurrencyType.MONEY))
    register(Currency.of("TRY", "Turkish Lira", 2, CurrencyType.MONEY))
    register(Currency.of("TTD", "Trinidad and Tobago Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("TWD", "New Taiwan Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("TZS", "Tanzanian Shilling", 2, CurrencyType.MONEY))
    register(Currency.of("UAH", "Hryvnia", 2, CurrencyType.MONEY))
    register(Currency.of("UGX", "Uganda Shilling", 0, CurrencyType.MONEY))
    register(Currency.of("USD", "US Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("USN", "US Dollar (Next day)", 2, CurrencyType.MONEY))
    register(Currency.of("UYI", "Uruguay Peso en Unidades Indexadas", 0, CurrencyType.MONEY))
    register(Currency.of("UYU", "Peso Uruguayo", 2, CurrencyType.MONEY))
    register(Currency.of("UZS", "Uzbekistan Sum", 2, CurrencyType.MONEY))
    register(Currency.of("VEF", "Bolivar", 2, CurrencyType.MONEY))
    register(Currency.of("VND", "Dong", 0, CurrencyType.MONEY))
    register(Currency.of("VUV", "Vatu", 0, CurrencyType.MONEY))
    register(Currency.of("WST", "Tala", 2, CurrencyType.MONEY))
    register(Currency.of("XAF", "Central African CFA Franc BCEAO", 2, CurrencyType.MONEY))
    register(Currency.of("XAG", "Silver", -1, CurrencyType.METAL))
    register(Currency.of("XAU", "Gold", -1, CurrencyType.METAL))
    register(Currency.of("XCD", "East Caribbean Dollar", 2, CurrencyType.MONEY))
    register(Currency.of("XLM", "Stellar", -1, CurrencyType.CRYPTO))
    register(Currency.of("XMR", "Monero", -1, CurrencyType.CRYPTO))
    register(Currency.of("XOF", "West African CFA Franc BCEAO", 2, CurrencyType.MONEY))
    register(Currency.of("XPD", "Palladium", -1, CurrencyType.METAL))
    register(Currency.of("XPT", "Platinum", -1, CurrencyType.METAL))
    register(Currency.of("XRP", "Ripple", -1, CurrencyType.CRYPTO))
    register(Currency.of("XSU", "Sucre", -1, CurrencyType.MONEY))
    register(Currency.of("XUA", "ADB Unit of Account", -1, CurrencyType.MONEY))
    register(Currency.of("YER", "Yemeni Rial", 2, CurrencyType.MONEY))
    register(Currency.of("ZAR", "Rand", 2, CurrencyType.MONEY))
    register(Currency.of("ZEC", "Zcash", -1, CurrencyType.CRYPTO))
    register(Currency.of("ZMW", "Zambian Kwacha", 2, CurrencyType.MONEY))
    register(Currency.of("ZWL", "Zimbabwe Dollar", 2, CurrencyType.MONEY))
