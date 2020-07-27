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
"""Provides a strategy that never does any type inference."""
import inspect
from typing import Callable, Dict, Optional

from pynguin.typeinference.strategy import InferredSignature, TypeInferenceStrategy


# pylint: disable=too-few-public-methods
class NoTypeInferenceStrategy(TypeInferenceStrategy):
    """Provides a strategy that never does any type inference."""

    def infer_type_info(self, method: Callable) -> InferredSignature:
        signature = inspect.signature(method)
        parameters: Dict[str, Optional[type]] = {}
        for param_name in signature.parameters:
            if param_name == "self":
                continue
            parameters[param_name] = None
        return_type: Optional[type] = None

        return InferredSignature(
            signature=signature, parameters=parameters, return_type=return_type
        )
