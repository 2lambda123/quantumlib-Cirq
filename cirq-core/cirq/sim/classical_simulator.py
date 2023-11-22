# Copyright 2023 The Cirq Developers
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

from typing import Dict
from collections import defaultdict
from cirq.sim.simulator import SimulatesSamples
from cirq import ops, protocols
from cirq.study.resolver import ParamResolver
from cirq.circuits.circuit import AbstractCircuit
from cirq.ops.raw_types import Qid
import numpy as np


# class ClassicalStateSimulator(SimulatesSamples):
#     """A simulator that only accepts only gates with classical counterparts.

#     This simulator evolves a single state, using only gates that output a single state for each
#     input state. The simulator runs in linear time, at the cost of not supporting superposition.
#     It can be used to estimate costs and simulate circuits for simple non-quantum algorithms using
#     many more qubits than fully capable quantum simulators.

#     The supported gates are:
#         - cirq.X
#         - cirq.CNOT
#         - cirq.SWAP
#         - cirq.TOFFOLI
#         - cirq.measure

#     Args:
#         circuit: The circuit to simulate.
#         param_resolver: Parameters to run with the program.
#         repetitions: Number of times to repeat the run. It is expected that
#             this is validated greater than zero before calling this method.

#     Returns:
#         A dictionary mapping measurement keys to measurement results.

#     Raises:
#         ValueError: If one of the gates is not an X, CNOT, SWAP, TOFFOLI or a measurement.
#     """

#     def _run(
#         self, circuit: AbstractCircuit, param_resolver: ParamResolver, repetitions: int
#     ) -> Dict[str, np.ndarray]:
#         results_dict: Dict[str, np.ndarray] = {}
#         values_dict: Dict[Qid, int] = defaultdict(int)
#         param_resolver = param_resolver or ParamResolver({})
#         resolved_circuit = protocols.resolve_parameters(circuit, param_resolver)

#         for moment in resolved_circuit:
#             for op in moment:
#                 gate = op.gate
#                 if gate == ops.X:
#                     values_dict[op.qubits[0]] = 1 - values_dict[op.qubits[0]]

#                 elif (
#                     isinstance(gate, ops.CNotPowGate)
#                     and gate.exponent == 1
#                     and gate.global_shift == 0
#                 ):
#                     if values_dict[op.qubits[0]] == 1:
#                         values_dict[op.qubits[1]] = 1 - values_dict[op.qubits[1]]

#                 elif (
#                     isinstance(gate, ops.SwapPowGate)
#                     and gate.exponent == 1
#                     and gate.global_shift == 0
#                 ):
#                     hold_qubit = values_dict[op.qubits[1]]
#                     values_dict[op.qubits[1]] = values_dict[op.qubits[0]]
#                     values_dict[op.qubits[0]] = hold_qubit

#                 elif (
#                     isinstance(gate, ops.CCXPowGate)
#                     and gate.exponent == 1
#                     and gate.global_shift == 0
#                 ):
#                     if (values_dict[op.qubits[0]] == 1) and (values_dict[op.qubits[1]] == 1):
#                         values_dict[op.qubits[2]] = 1 - values_dict[op.qubits[2]]

#                 elif isinstance(gate, ops.MeasurementGate):
#                     qubits_in_order = op.qubits
#                     # add the new instance of a key to the numpy array in results dictionary
#                     if gate.key in results_dict:
#                         shape = len(qubits_in_order)
#                         current_array = results_dict[gate.key]
#                         new_instance = np.zeros(shape, dtype=np.uint8)
#                         for bits in range(0, len(qubits_in_order)):
#                             new_instance[bits] = values_dict[qubits_in_order[bits]]
#                             results_dict[gate.key] = np.insert(
#                                 current_array, len(current_array[0]), new_instance, axis=1
#                             )
#                     else:
#                         # create the array for the results dictionary
#                         new_array_shape = (repetitions, 1, len(qubits_in_order))
#                         new_array = np.zeros(new_array_shape, dtype=np.uint8)
#                         for reps in range(0, repetitions):
#                             for instances in range(1):
#                                 for bits in range(0, len(qubits_in_order)):
#                                     new_array[reps][instances][bits] = values_dict[
#                                         qubits_in_order[bits]
#                                     ]
#                         results_dict[gate.key] = new_array

#                 elif not (
#                     (isinstance(gate, ops.XPowGate) and gate.exponent == 0)
#                     or (isinstance(gate, ops.CCXPowGate) and gate.exponent == 0)
#                     or (isinstance(gate, ops.SwapPowGate) and gate.exponent == 0)
#                     or (isinstance(gate, ops.CNotPowGate) and gate.exponent == 0)
#                 ):
#                     raise ValueError(
#                         "Can not simulate gates other than cirq.XGate, "
#                         + "cirq.CNOT, cirq.SWAP, and cirq.CCNOT"
#                     )

#         return results_dict

#TODO: study example custom class and compare information

class ClassicalBasisState(cirq.qis.QuantumStateRepresentation):
    def __init__(self, initial_state: List[int]):
        self.basis = initial_state

    def copy(self, deep_copy_buffers: bool = True) -> 'ComputationalBasisState':
        return ClassicalBasisState(self.basis)

    def measure(self, axes: Sequence[int], seed: 'cirq.RANDOM_STATE_OR_SEED_LIKE' = None):
        return [self.basis[i] for i in axes]


class ClassicalBasisSimState(cirq.SimulationState[ClassicalBasisState]):
    def __init__(self, initial_state, qubits, classical_data):
        state = ClassicalBasisState(
            cirq.big_endian_int_to_bits(initial_state, bit_count=len(qubits))
        )
        super().__init__(state=state, qubits=qubits, classical_data=classical_data)

    def _act_on_fallback_(self, action, qubits: Sequence[cirq.Qid], allow_decompose: bool = True):
        gate = action.gate if isinstance(action, ops.Operation) else action
        if isinstance(gate, ops.X):
            q1 = self.qubit_map[qubits[0]]
            self._state.basis[q1] = int(1 - self._state.basis[q1])
            return True

        elif isinstance(gate, cirq.XPowGate):
            q1 = self.qubit_map[qubits[0]]
            self._state.basis[i] = int(gate.exponent + self._state.basis[q1]) % qubits[0].dimension
            return True

        elif isinstance(gate, ops.CNotPowGate):
            q1_i = self.qubit_map[qubits[0]]
            q2_i = self.qubit_map[qubits[1]]
            if self._state.basis[q1_i]:
                self._state.basis[q2_i] =  int(gate.exponent + self._state.basis[q2_i]) % qubits[1].dimension
            return True

        elif isinstance(gate, ops.SwapPowGate):
            self.qubit_map[qubits[0]], self.qubit_map[qubits[1]] = self.qubit_map[qubits[1]], self.qubit_map[qubits[0]] 
            return True

        elif isinstance(gate, ops.CCXPowGate):
            q1_i = self.qubit_map[op.qubits[0]]
            q2_i = self.qubit_map[op.qubits[1]]
            q3_i = self.qubit_map[op.qubits[2]]
            if self._state.basis[q1_i] and self._state.basis[q2_i]:
                self._state.basis[q3_i] = int(gate.exponent + self._state.basis[q3_i]) % qubits[2].dimension
            return True

        else:
            return False
