import functools
import multiprocessing as mp
import operator
from typing import Dict, List
from unittest.mock import MagicMock, NonCallableMagicMock

import pytest

import flutes
from .utils import check_iterator


def sqr(x: int) -> int:
    return x * x


def test_safe_pool() -> None:
    seq = list(range(10000))
    target = list(map(sqr, seq))  # sequential
    with mp.Pool(1) as pool:
        pool_type = type(pool)

    file_obj = MagicMock()
    with flutes.safe_pool(0, closing=[file_obj]) as pool:
        assert type(pool) is not pool_type
        check_iterator(pool.imap(sqr, seq), target)
    file_obj.assert_called_once()

    file_obj = NonCallableMagicMock()
    file_obj.mock_add_spec(["close"])
    with flutes.safe_pool(2, closing=[file_obj]) as pool:
        assert type(pool) is pool_type
        check_iterator(pool.imap(sqr, seq), target)
        raise ValueError  # should swallow exceptions
    file_obj.close.assert_called_once()


class PoolState(flutes.PoolState):
    def __init__(self, large_dict: Dict[str, int]):
        self.large_dict = large_dict

    def convert(self, x: str) -> int:
        return self.large_dict[x]


def test_stateful_pool() -> None:
    large_dict = {str(i): i for i in range(100000)}
    seq = list(map(str, range(100000)))
    target = sum(map(int, seq))  # sequential

    for n_procs in [0, 2]:
        with flutes.safe_pool(n_procs, state_class=PoolState, init_args=(large_dict,)) as pool:
            result = sum(pool.imap_unordered(PoolState.convert, seq, chunksize=1000))

            # See, if you had a type checker, you wouldn't be making these mistakes.
            with pytest.raises(ValueError, match="Bound methods of the pool state class"):
                _ = sum(pool.imap_unordered(PoolState({}).convert, seq, chunksize=1000))  # type: ignore[arg-type]
            with pytest.raises(ValueError, match="Only unbound methods of the pool state class"):
                _ = sum(pool.imap_unordered(PoolState2.generate, seq, chunksize=1000))  # type: ignore[arg-type]
        assert result == target


class PoolState2(flutes.PoolState):
    def __init__(self):
        self.numbers: List[int] = []

    def generate(self, start: int, stop: int) -> None:
        for x in range(start, stop):
            self.numbers.append(x)


def test_stateful_pool_get_state() -> None:
    for n_procs in [0, 2]:
        with flutes.safe_pool(n_procs, state_class=PoolState2) as pool:
            intervals = list(range(0, 100 + 1, 5))
            pool.starmap(PoolState2.generate, zip(intervals, intervals[1:]))
            states = pool.get_states()
            assert sorted(x for state in states for x in state.numbers) == list(range(100))


def test_pool_methods() -> None:
    seq = list(range(10000))
    target = list(map(sqr, seq))  # sequential
    for n_procs in [0, 2]:
        for state_class in [PoolState, None]:
            with flutes.safe_pool(n_procs, state_class=state_class, init_args=(None,)) as pool:
                check_iterator(pool.map(sqr, seq), target)
                check_iterator(pool.imap(sqr, seq), target)
                check_iterator(sorted(pool.imap_unordered(sqr, seq)), target)
                check_iterator(pool.starmap(operator.mul, zip(seq, seq)), target)
                check_iterator(pool.map_async(sqr, seq).get(), target)
                check_iterator(pool.starmap_async(operator.mul, zip(seq, seq)).get(), target)
                assert pool.apply(sqr, (10,)) == 100
                assert pool.apply_async(sqr, (10,)).get() == 100


def progress_bar_fn(idx: int, bar) -> None:
    total = (idx + 1) * 2
    bar.new(desc=f"Bar {idx}", total=total)
    for i in range(total):
        bar.update(1, postfix={"i": i})
        if i % 5 == 1:
            flutes.log(f"test {i}")
    for i in bar.iter(range(total)):
        bar.update(postfix={"i": i})


def test_ProgressBarManager() -> None:
    for proc in [0, 2]:
        # Test multiprocessing in `proc = 2`
        # Test coverage in `proc = 0`
        manager = flutes.ProgressBarManager()
        with flutes.safe_pool(proc, closing=[manager]) as pool:
            fn = functools.partial(progress_bar_fn, bar=manager.proxy)
            pool.map(fn, range(10))
