# Copyright 2019 The Cirq Developers
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
"""ISWAPPowGate conjugated by tensor product Rz(phi) and Rz(-phi)."""

from typing import List, Union, Sequence, Tuple, Optional

import numpy as np
import sympy

import cirq
from cirq import value, protocols
from cirq._compat import proper_repr
from cirq.ops import common_gates, eigen_gate, op_tree, gate_features, raw_types
from cirq.value import type_alias


@value.value_equality(manual_cls=True)
class PhasedISwapPowGate(eigen_gate.EigenGate, gate_features.TwoQubitGate):
    """Fractional ISWAP conjugated by Z rotations.

    PhasedISwapPowGate with phase_exponent p and exponent t is equivalent to
    the composition

        (Z^-p ⊗ Z^p) ISWAP^t (Z^p ⊗ Z^-p)

    and is given by the matrix:

        [[1, 0, 0, 0],
         [0, c, i·s·f, 0],
         [0, i·s·f*, c, 0],
         [0, 0, 0, 1]]

    where:

        c = cos(π·t/2)
        s = sin(π·t/2)
        f = exp(2πi·p)

    and star indicates complex conjugate.
    """

    def __init__(self,
                 *,
                 phase_exponent: Union[float, sympy.Symbol] = 0.25,
                 exponent: Union[float, sympy.Symbol] = 1.0,
                 global_shift: float = 0.0) -> None:
        """
        Args:
            phase_exponent: The exponent on the Z gates. We conjugate by
                the T gate by default.
            exponent: The exponent on the ISWAP gate, see EigenGate for
                details.
            global_shift: How much to shift the operation's eigenvalues at
                exponent=1, see EigenGate for details.
        """
        self._phase_exponent = value.canonicalize_half_turns(phase_exponent)
        self._iswap = common_gates.ISwapPowGate(exponent=exponent,
                                                global_shift=global_shift)
        super().__init__(exponent=exponent, global_shift=global_shift)

    @property
    def phase_exponent(self) -> Union[float, sympy.Symbol]:
        return self._phase_exponent

    def _json_dict_(self):
        return {
            'cirq_type': self.__class__.__name__,
            'phase_exponent': self._phase_exponent,
            'exponent': self._exponent,
            'global_shift': self._global_shift,
        }

    def _value_equality_values_cls_(self):
        if self.phase_exponent == 0:
            return common_gates.ISwapPowGate
        return PhasedISwapPowGate

    def _value_equality_values_(self):
        if self.phase_exponent == 0:
            return self._iswap._value_equality_values_()
        return (self.phase_exponent, *self._iswap._value_equality_values_())

    def _is_parameterized_(self) -> bool:
        if protocols.is_parameterized(self._iswap):
            return True
        return protocols.is_parameterized(self._phase_exponent)

    def _with_exponent(self,
                       exponent: type_alias.TParamVal) -> 'PhasedISwapPowGate':
        return PhasedISwapPowGate(phase_exponent=self.phase_exponent,
                                  exponent=exponent,
                                  global_shift=self.global_shift)

    def _eigen_shifts(self) -> List[float]:
        return [0.0, +0.5, -0.5]

    def _eigen_components(self):
        phase = np.exp(1j * np.pi * self.phase_exponent)
        phase_matrix = np.diag([1, phase, phase.conjugate(), 1])
        inverse_phase_matrix = np.conjugate(phase_matrix)
        eigen_components: List[Tuple[float, np.ndarray]] = []
        for eigenvalue, projector in self._iswap._eigen_components():
            new_projector = phase_matrix @ projector @ inverse_phase_matrix
            eigen_components.append((eigenvalue, new_projector))
        return eigen_components

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Optional[np.ndarray]:
        if protocols.is_parameterized(self):
            return NotImplemented
        if self.exponent != 1:
            return NotImplemented

        phase = np.exp(1j * np.pi * self.phase_exponent)
        zo = args.subspace_index(0b01)
        oz = args.subspace_index(0b10)
        args.target_tensor[zo] *= phase
        args.target_tensor[oz] *= phase.conjugate()
        args.target_tensor = self._iswap._apply_unitary_(args)
        assert args.target_tensor is not None
        args.target_tensor[zo] *= phase.conjugate()
        args.target_tensor[oz] *= phase
        return args.target_tensor

    def _decompose_(self, qubits: Sequence[raw_types.Qid]) -> op_tree.OP_TREE:
        if len(qubits) != 2:
            raise ValueError(f'Expected two qubits, got {len(qubits)}')
        a, b = qubits

        yield cirq.Z(a)**self.phase_exponent
        yield cirq.Z(b)**-self.phase_exponent
        yield from protocols.decompose_once_with_qubits(self._iswap, qubits)
        yield cirq.Z(a)**-self.phase_exponent
        yield cirq.Z(b)**self.phase_exponent

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if self._is_parameterized_():
            return NotImplemented
        expansion = protocols.pauli_expansion(self._iswap)
        assert set(expansion.keys()).issubset({'II', 'XX', 'YY', 'ZZ'})
        assert np.isclose(expansion['XX'], expansion['YY'])

        v = (expansion['XX'] + expansion['YY']) / 2
        phase_angle = np.pi * self.phase_exponent
        c, s = np.cos(2 * phase_angle), np.sin(2 * phase_angle)

        return value.LinearDict({
            'II': expansion['II'],
            'XX': c * v,
            'YY': c * v,
            'XY': s * v,
            'YX': -s * v,
            'ZZ': expansion['ZZ'],
        })

    def __str__(self) -> str:
        if self.exponent == 1:
            return 'PhasedISWAP'
        return f'PhasedISWAP**{self.exponent}'

    def __repr__(self):
        phase_exponent = proper_repr(self._phase_exponent)
        args = [f'phase_exponent={phase_exponent}']
        if self.exponent != 1:
            exponent = proper_repr(self.exponent)
            args.append(f'exponent={exponent}')
        if self._global_shift != 0:
            global_shift = proper_repr(self._global_shift)
            args.append(f'global_shift={global_shift}')
        arg_string = ', '.join(args)
        return f'cirq.PhasedISwapPowGate({arg_string})'


# The ISWAP gate conjugated by T⊗T^-1.
#
# Matrix of GivensRotation^t is
#
#     [[1, 0, 0, 0],
#      [0, c, -s, 0],
#      [0, s, c, 0],
#      [0, 0, 0, 1]]
#
# where
#
#     c = cos(π·t/2),
#     s = sin(π·t/2).
#
# Equivalently, it may be defined as
#
#     GivensRotation^t ≡ exp(-i π t (Y⊗X - X⊗Y) / 4)
#
GivensRotation = PhasedISwapPowGate()
