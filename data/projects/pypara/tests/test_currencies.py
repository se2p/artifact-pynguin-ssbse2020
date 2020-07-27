from pypara.currencies import Currencies


def test_order() -> None:
    ## Get two currency instances:
    ccy1 = Currencies["USD"]
    ccy2 = Currencies["EUR"]

    ## Test:
    assert ccy1 == ccy1
    assert ccy1 > ccy2
    assert sorted([ccy1, ccy2]) == [ccy2, ccy1]
