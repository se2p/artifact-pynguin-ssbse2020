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
from unittest.mock import MagicMock

import pynguin.testcase.statements.assignmentstatement as astmt
import pynguin.testcase.variable.variablereferenceimpl as vri


def test_field_statement(test_case_mock, variable_reference_mock):
    rhs = MagicMock(vri.VariableReferenceImpl)
    field_statement = astmt.AssignmentStatement(
        test_case_mock, variable_reference_mock, rhs
    )
    assert field_statement._rhs == rhs


def test_hash(test_case_mock, variable_reference_mock):
    statement = astmt.AssignmentStatement(
        test_case_mock, variable_reference_mock, MagicMock(vri.VariableReferenceImpl)
    )
    assert statement.__hash__() != 0


def test_eq_same(test_case_mock, variable_reference_mock):
    statement = astmt.AssignmentStatement(
        test_case_mock, variable_reference_mock, MagicMock(vri.VariableReferenceImpl)
    )
    assert statement.__eq__(statement)


def test_eq_other_type(test_case_mock, variable_reference_mock):
    statement = astmt.AssignmentStatement(
        test_case_mock, variable_reference_mock, MagicMock(vri.VariableReferenceImpl)
    )
    assert not statement.__eq__(test_case_mock)


def test_accept(test_case_mock, variable_reference_mock):
    statement = astmt.AssignmentStatement(
        test_case_mock, variable_reference_mock, variable_reference_mock
    )
    visitor = MagicMock()
    statement.accept(visitor)
    visitor.visit_assignment_statement.assert_called_with(statement)
