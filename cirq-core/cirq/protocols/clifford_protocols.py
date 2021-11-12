# Copyright 2021 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import (
    Any,
    Sequence,
    Union,
    TYPE_CHECKING,
)

import numpy as np
from typing_extensions import Protocol

from cirq._doc import doc_private
from cirq.type_workarounds import NotImplementedType

if TYPE_CHECKING:
    import cirq


class SupportsApplyToTableau(Protocol):
    """An object that can apply a transformation to a Clifford tableau."""

    @doc_private
    def _apply_to_tableau_(
        self, tableau: 'cirq.CliffordTableau', axes: Sequence[int], prng: np.random.RandomState
    ) -> Union[bool, NotImplementedType]:
        """Applies a transform to the given Clifford tableau.

        Args:
            tableau: A Clifford tableau that is the target of the transform.
            axes: The axes to which the transform should be applied.
            prng: A random number generator to use if necessary.

        Returns:
            True: The receiving object (`self`) could apply a transform.
            NotImplemented: The receiving object cannot apply a transform.

            All other return values are considered to be errors.
        """


def apply_to_tableau(
    val: Any,
    tableau: 'cirq.CliffordTableau',
    axes: Sequence[int],
    prng: np.random.RandomState,
) -> Union[bool, NotImplementedType]:
    """Applies a transform to the given Clifford tableau.

    Args:
        val: The object (typically a gate) that contains a transform to apply.
        tableau: A Clifford tableau that is the target of the transform.
        axes: The axes to which the transform should be applied.
        prng: The random number generator to use if necessary.

    Returns:
        True: The receiving object (`self`) could apply a transform.
        NotImplemented: The receiving object cannot apply a transform.

        All other return values are considered to be errors.
    """
    getter = getattr(val, '_apply_to_tableau_', None)
    return NotImplemented if getter is None else getter(tableau, axes, prng)


class SupportsApplyToChForm(Protocol):
    @doc_private
    def _apply_to_ch_form_(
        self, state: 'cirq.StabilizerStateChForm', axes: Sequence[int], prng: np.random.RandomState
    ) -> Union[bool, NotImplementedType]:
        """Applies a transform to the given Clifford CH-form.

        Args:
            state: A Clifford CH-form that is the target of the transform.
            axes: The axes to which the transform should be applied.
            prng: The random number generator to use if necessary.

        Returns:
            True: The receiving object (`self`) could apply a transform.
            NotImplemented: The receiving object cannot apply a transform.

            All other return values are considered to be errors.
        """


def apply_to_ch_form(
    val: Any,
    state: 'cirq.StabilizerStateChForm',
    axes: Sequence[int],
    prng: np.random.RandomState,
) -> Union[bool, NotImplementedType]:
    """Applies a transform to the given Clifford CH-form.

    Args:
        val: The object (typically a gate) that contains a transform to apply.
        state: A Clifford CH-form that is the target of the transform.
        axes: The axes to which the transform should be applied.
        prng: A random number generator to use if necessary.

    Returns:
        True: The receiving object (`self`) could apply a transform.
        NotImplemented: The receiving object cannot apply a transform.

        All other return values are considered to be errors.
    """
    getter = getattr(val, '_apply_to_ch_form_', None)
    return NotImplemented if getter is None else getter(state, axes, prng)
