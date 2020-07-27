# This file is part of Pynguin.
#
# Pynguin is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pynguin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pynguin.  If not, see <https://www.gnu.org/licenses/>.
from typing import List, Tuple
from unittest.mock import MagicMock

import pytest

import pynguin.configuration as config
import pynguin.testcase.statements.statement as stmt
import pynguin.testcase.testcase as tc
from pynguin.generation.algorithms.testgenerationstrategy import TestGenerationStrategy
from pynguin.generation.stoppingconditions.maxiterationsstoppingcondition import (
    MaxIterationsStoppingCondition,
)
from pynguin.generation.stoppingconditions.maxtestsstoppingcondition import (
    MaxTestsStoppingCondition,
)
from pynguin.generation.stoppingconditions.maxtimestoppingcondition import (
    MaxTimeStoppingCondition,
)
from pynguin.generation.stoppingconditions.stoppingcondition import StoppingCondition
from pynguin.setup.testcluster import TestCluster


class _TestGenerationStrategy(TestGenerationStrategy):
    def __init__(self):
        super().__init__(MagicMock(), MagicMock(TestCluster))

    def generate_sequences(self) -> Tuple[List[tc.TestCase], List[tc.TestCase]]:
        raise NotImplementedError(
            "This class is not intended for usage but only for testing"
        )


@pytest.fixture
def algorithm():
    return _TestGenerationStrategy()


def test_not_has_type_violations(algorithm):
    assert not algorithm.has_type_violations([])


def test_has_type_violations(algorithm):
    assert algorithm.has_type_violations([Exception(), TypeError(), AttributeError()])


def test_purge_test_cases_without_threshold(algorithm, test_case_mock):
    config.INSTANCE.counter_threshold = 0
    purged, remaining = algorithm.purge_test_cases([test_case_mock])
    assert purged == []
    assert remaining == [test_case_mock]


def test_purge_test_cases(algorithm):
    config.INSTANCE.counter_threshold = 1
    tc_1 = MagicMock(tc.TestCase)
    tc_1.statements = [MagicMock(stmt.Statement)]
    tc_2 = MagicMock(tc.TestCase)
    tc_2.statements = [MagicMock(stmt.Statement), MagicMock(stmt.Statement)]
    purged, remaining = algorithm.purge_test_cases([tc_1, tc_2])
    assert purged == [tc_2]
    assert remaining == [tc_1]


def test_is_fulfilled(algorithm):
    stopping_condition = MagicMock(StoppingCondition)
    stopping_condition.is_fulfilled.return_value = True
    assert algorithm.is_fulfilled(stopping_condition)


def test_is_not_fulfilled(algorithm):
    stopping_condition = MagicMock(StoppingCondition)
    stopping_condition.is_fulfilled.return_value = False
    assert not algorithm.is_fulfilled(stopping_condition)


@pytest.mark.parametrize(
    "configuration,result",
    [
        pytest.param(config.StoppingCondition.MAX_TIME, MaxTimeStoppingCondition),
        pytest.param(config.StoppingCondition.MAX_TESTS, MaxTestsStoppingCondition),
        pytest.param(
            config.StoppingCondition.MAX_ITERATIONS, MaxIterationsStoppingCondition
        ),
        pytest.param("foo", MaxTimeStoppingCondition),
    ],
)
def test_get_stopping_condition(configuration, result, algorithm):
    config.INSTANCE.stopping_condition = configuration
    condition = algorithm.get_stopping_condition()
    assert isinstance(condition, result)
