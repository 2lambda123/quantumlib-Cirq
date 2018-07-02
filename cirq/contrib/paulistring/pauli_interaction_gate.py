# Copyright 2018 The Cirq Developers
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

from typing import Hashable, List, Optional, Sequence, Tuple, Union

import numpy as np

from cirq import ops, value

from cirq.contrib.paulistring import Pauli, CliffordGate


pauli_eigen_map = {
    Pauli.X: (np.array([[0.5,  0.5 ], [0.5,   0.5]]),
              np.array([[0.5, -0.5 ], [-0.5,  0.5]])),
    Pauli.Y: (np.array([[0.5, -0.5j], [0.5j,  0.5]]),
              np.array([[0.5,  0.5j], [-0.5j, 0.5]])),
    Pauli.Z: (np.diag([1, 0]),
              np.diag([0, 1])),
}


class PauliInteractionGate(ops.EigenGate,
                           ops.CompositeGate,
                           ops.InterchangeableQubitsGate,
                           ops.TextDiagrammableGate):
    def __init__(self,
                 pauli0: Pauli, invert0: bool,
                 pauli1: Pauli, invert1: bool,
                 *,
                 half_turns: Optional[Union[value.Symbol, float]] = None,
                 rads: Optional[float] = None,
                 degs: Optional[float] = None) -> None:
        """At most one angle argument may be specified. If more are specified,
        the result is considered ambiguous and an error is thrown. If no angle
        argument is given, the default value of one half turn is used.

        Args:
            half_turns: Relative phasing of the interaction's eigenstates, in
                half_turns.
            rads: Relative phasing of the interaction's eigenstates, in radians.
            degs: Relative phasing of the interaction's eigenstates, in degrees.
        """
        super().__init__(exponent=value.chosen_angle_to_half_turns(
            half_turns=half_turns,
            rads=rads,
            degs=degs))
        self.pauli0 = pauli0
        self.invert0 = invert0
        self.pauli1 = pauli1
        self.invert1 = invert1

    def _eq_tuple(self) -> Tuple[Hashable, ...]:
        return (PauliInteractionGate,
                self.pauli0, self.invert0,
                self.pauli1, self.invert1,
                self._exponent)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._eq_tuple())

    def qubit_index_to_equivalence_group_key(self, index: int) -> int:
        if self.pauli0 == self.pauli1 and self.invert0 == self.invert1:
            return 0
        else:
            return index

    def _canonical_exponent_period(self) -> Optional[float]:
        return 2

    def _with_exponent(self, exponent: Union[value.Symbol, float]
                       ) -> 'PauliInteractionGate':
        return PauliInteractionGate(self.pauli0, self.invert0,
                                    self.pauli1, self.invert1,
                                    half_turns=exponent)

    def _eigen_components(self) -> List[Tuple[float, np.ndarray]]:
        def yield_components():
            for q0_index, q1_index in ((0, 0), (0, 1), (1, 0), (1, 1)):
                q0_comp = pauli_eigen_map[self.pauli0][q0_index ^ self.invert0]
                q1_comp = pauli_eigen_map[self.pauli1][q1_index ^ self.invert1]
                component = np.kron(q0_comp, q1_comp)
                phase = 1 if q0_index and q1_index else 0
                yield (phase, component)
        return list(yield_components())

    def default_decompose(self, qubits: Sequence[ops.QubitId]
                          ) -> ops.op_tree.OP_TREE:
        q0, q1 = qubits
        right_gate0 = CliffordGate.from_single_map(
                                    z_to=(self.pauli0, self.invert0))
        right_gate1 = CliffordGate.from_single_map(
                                    z_to=(self.pauli1, self.invert1))
        left_gate0 = right_gate0.inverse()
        left_gate1 = right_gate1.inverse()
        yield left_gate0(q0)
        yield left_gate1(q1)
        yield ops.Rot11Gate(half_turns=self._exponent)(q0, q1)
        yield right_gate0(q0)
        yield right_gate1(q1)

    def text_diagram_wire_symbols(self,
                                  qubit_count: Optional[int] = None,
                                  use_unicode_characters: bool = True,
                                  precision: Optional[int] = 3
                                  ) -> Tuple[str, ...]:
        labels = {Pauli.X: 'X', Pauli.Y: 'Y', Pauli.Z: '@'}
        l0 = labels[self.pauli0]
        l1 = labels[self.pauli1]
        # Add brackets around letter if inverted
        l0, l1 = ('[-{}]'.format(l) if inv else l
                  for l, inv in ((l0, self.invert0), (l1, self.invert1)))
        return l0, l1

    def text_diagram_exponent(self) -> Union[float, value.Symbol]:
        return self._exponent

    def __repr__(self):
        return 'PauliInteractionGate({}{!s}, {}{!s})'.format(
               '+-'[self.invert0], self.pauli0, '+-'[self.invert1], self.pauli1)
