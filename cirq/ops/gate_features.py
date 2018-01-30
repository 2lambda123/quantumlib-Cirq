# Copyright 2017 Google LLC
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

"""Marker classes for indicating which additional features gates support.

For example: some gates are reversible, some have known matrices, etc.
"""

import abc

import numpy as np
from typing import Sequence, Tuple

from cirq.ops import op_tree
from cirq.ops import raw_types


class ReversibleGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate whose effect can be undone in a known way.

    Examples: The S gate, the CZ gate, and the H gate.
    Anti-examples: The measurement gate.
    """

    @abc.abstractmethod
    def inverse(self) -> 'ReversibleGate':
        """Returns a gate with an exactly opposite effect."""
        pass


class ExtrapolatableGate(ReversibleGate, metaclass=abc.ABCMeta):
    """A gate whose effect can be continuously scaled up/down/negated.

    Examples: The Z gate, the Z**0.5 gate, the CZ gate, and the H gate.
    Anti-examples: The measurement gate, and abstract gates representing
        operations where it is not tractable to compute the scaled effect.
    """

    @abc.abstractmethod
    def extrapolate_effect(self, factor: float) -> 'ExtrapolatableGate':
        """Augments, diminishes, or reverses the effect of the receiving gate.

        Args:
            factor: The amount to scale the gate's effect by.

        Returns:
            A gate equivalent to applying the receiving gate 'factor' times.
        """
        pass

    def __pow__(self, power: float) -> 'ExtrapolatableGate':
        """Extrapolates the effect of the gate.

        Note that there are cases where (G**a)**b != G**(a*b). For example,
        start with a 90 degree rotation then cube it then raise it to a
        non-integer power such as 3/2. Assuming that rotations are always
        normalized into the range (-180, 180], note that:

            ((rot 90)**3)**1.5 = (rot 270)**1.5 = (rot -90)**1.5 = rot -135

        but

            (rot 90)**(3*1.5) = (rot 90)**4.5 = rot 405 = rot 35

        Because normalization discards the winding number.

        Args:
          power: The extrapolation factor.

        Returns:
          A gate with the extrapolated effect.
        """
        return self.extrapolate_effect(power)

    def inverse(self) -> 'ExtrapolatableGate':
        return self.extrapolate_effect(-1)


class SelfInverseGate(ReversibleGate):
    """A reversible gate that is its own inverse.

    Examples: The Z gate, the X gate, and the CZ gate.
    Anti-examples: The S gate and the measurement gate."""

    def inverse(self) -> 'SelfInverseGate':
        return self


class CompositeGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate with a known decomposition into 'simpler' gates."""

    @abc.abstractmethod
    def default_decompose(
            self, qubits: Sequence[raw_types.QubitId]) -> op_tree.OP_TREE:
        """Yields operations for performing this gate on the given qubits.

        Args:
            qubits: The qubits the operation should be applied to.
        """
        pass


class KnownMatrixGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate whose effect is described by a matrix.

    Examples: The H gate, the CZ gate, and the S gate.
    Anti-examples: The measurement gate, sweep-parameterized gates, and gates
        with matrices too big to be useful.
    """

    @abc.abstractmethod
    def matrix(self) -> np.ndarray:
        """The unitary matrix of the operation this gate applies."""
        pass


class AsciiDiagrammableGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate whose constant non-parameterized effect has a known matrix."""

    # noinspection PyMethodMayBeStatic
    def ascii_exponent(self) -> float:
        """The exponent to modify the gate symbol with. 1 means no modifier."""
        return 1

    @abc.abstractmethod
    def ascii_wire_symbols(self) -> Tuple[str, ...]:
        """The symbols that should be shown on the gate's qubits (in order)."""
        pass


class PhaseableGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate whose effect can be phased in the computational basis.

    When this is implemented by a gate, phase operations can be moved across
    the gate by phasing it when doing so.

    Examples: The ExpW gate, the CZ gate (no effect).
    Anti-examples: The CNOT gate.
    """

    @abc.abstractmethod
    def phase_by(self,
                 phase_turns: float,
                 qubit_index: int) -> 'PhaseableGate':
        """Returns a phased version of the gate.

        Args:
            phase_turns: The amount to phase the gate, in fractions of a
                whole turn.
            qubit_index: The index of the target qubit the phasing applies
                to.

        Returns:
            The phased gate.
        """
        pass


class PhaseSinkGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate whose effect can absorb phasing in the computational basis.

    When this is implemented by a gate, phase operations can be moved into
    the gate by sinking phase into it.

    Examples: Measurement, the parametrized ExpZ gate.
    Anti-examples: The X gate, the CZ gate.
    """

    @abc.abstractmethod
    def absorb_phase_by(self,
                        phase_turns: float,
                        qubit_index: int) -> 'PhaseSinkGate':
        """Returns a phased version of the gate.

        Args:
            phase_turns: The amount to phase the gate, in fractions of a whole
                turn.
            qubit_index: The index of the target qubit the phasing applies to.

        Returns:
            The phased gate.
        """
        pass


class BoundedEffectGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate whose effect on the state is known to be below some threshold."""

    @abc.abstractmethod
    def trace_distance_bound(self) -> np.ndarray:
        """A maximum on the trace distance between this gate's input/output.

        Approximations that overestimate are permitted. Even ones that exceed
        1. Underestimates are not permitted. Generally this method is used
        when deciding whether to keep gates, so only the behavior near 0 is
        important.
        """
        pass


class ConstantSingleQubitGate(KnownMatrixGate, metaclass=abc.ABCMeta):
    """A gate that applies a known constant effect to one qubit."""

    def validate_args(self, qubits):
        if len(qubits) != 1:
            raise ValueError(
                'Single-qubit gate applied to multiple qubits: {}({})'.
                format(self, qubits))


class ConstantAdjacentTwoQubitGate(KnownMatrixGate, metaclass=abc.ABCMeta):
    """A gate that applies a known constant effect to adjacent qubits."""

    def validate_args(self, qubits):
        if len(qubits) != 2:
            raise ValueError(
                'Two-qubit gate not applied to two qubits: {}({})'.
                format(self, qubits))

        if not qubits[0].is_adjacent(qubits[1]):
            raise ValueError(
                'Two-qubit gate applied to non-adjacent qubits: {}({})'.
                format(self, qubits))
