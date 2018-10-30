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

from typing import Optional

import numpy as np

from cirq import ops, linalg, decompositions, protocols
from cirq.circuits.circuit import Circuit
from cirq.circuits.optimization_pass import (
    PointOptimizationSummary,
    PointOptimizer,
)


class ConvertToSingleQubitCliffordGates(PointOptimizer):
    """Attempts to convert single-qubit gates into single-qubit
    SingleQubitCliffordGates.

    First, checks if the operation has a known unitary effect. If so, and the
        gate is a 1-qubit gate, then decomposes it and tries to make a
        SingleQubitCliffordGate. It fails if the operation is not in the
    Clifford group.

    Second, attempts to `cirq.decompose` to the operation.
    """

    def __init__(self,
                 ignore_failures: bool = False,
                 tolerance: float = 0) -> None:
        """
        Args:
            ignore_failures: If set, gates that fail to convert are forwarded
                unchanged. If not set, conversion failures raise a TypeError.
            tolerance: Maximum absolute error tolerance. The optimization is
                permitted to round angles with a threshold determined by this
                tolerance.
        """
        super().__init__()
        self.ignore_failures = ignore_failures
        self.tolerance = tolerance
        self._tol = linalg.Tolerance(atol=tolerance)

    def _rotation_to_clifford_gate(self, pauli: ops.Pauli, half_turns: float
                                   ) -> ops.SingleQubitCliffordGate:
        quarter_turns = round(half_turns * 2) % 4
        if quarter_turns == 1:
            return ops.SingleQubitCliffordGate.from_pauli(pauli, True)
        elif quarter_turns == 2:
            return ops.SingleQubitCliffordGate.from_pauli(pauli)
        elif quarter_turns == 3:
            return ops.SingleQubitCliffordGate.from_pauli(pauli, True)**-1
        else:
            return ops.SingleQubitCliffordGate.I

    def _matrix_to_clifford_op(self, mat: np.ndarray, qubit: ops.QubitId
                               ) -> Optional[ops.Operation]:
        rotations = decompositions.single_qubit_matrix_to_pauli_rotations(
                                       mat, self.tolerance)
        clifford_gate = ops.SingleQubitCliffordGate.I
        for pauli, half_turns in rotations:
            if self._tol.all_near_zero_mod(half_turns, 0.5):
                clifford_gate = clifford_gate.merged_with(
                    self._rotation_to_clifford_gate(pauli, half_turns))
            else:
                return None
        return clifford_gate(qubit)

    def convert(self, op: ops.Operation) -> ops.OP_TREE:
        def keep(op: ops.Operation) -> bool:
            # Don't change if it's already a SingleQubitCliffordGate
            return (isinstance(op, ops.GateOperation) and
                    isinstance(op.gate, ops.SingleQubitCliffordGate))

        def convert_one(op: ops.Operation) -> ops.OP_TREE:
            # Single qubit gate with known matrix?
            if len(op.qubits) == 1:
                mat = protocols.unitary(op, None)
                if mat is not None:
                    cliff_op = self._matrix_to_clifford_op(mat, op.qubits[0])
                    if cliff_op is not None:
                        return cliff_op

            return NotImplemented

        def on_stuck_raise(op: ops.Operation):
            if len(op.qubits) == 1 and protocols.unitary(op, None) is not None:
                raise ValueError('Single qubit operation is not in the '
                                  'Clifford group: {!r}'.format(op))

            raise TypeError("Don't know how to work with {!r}. "
                            "It isn't composite or a 1-qubit operation "
                            "with a known unitary effect.".format(op))

        return protocols.decompose(op, intercepting_decomposer=convert_one,
                                   keep=keep,
                                   on_stuck_raise=(None if self.ignore_failures
                                                   else on_stuck_raise))

    def optimization_at(self, circuit: Circuit, index: int, op: ops.Operation
                        ) -> Optional[PointOptimizationSummary]:
        converted = self.convert(op)
        if converted is op:
            return None

        return PointOptimizationSummary(
            clear_span=1,
            new_operations=converted,
            clear_qubits=op.qubits)
