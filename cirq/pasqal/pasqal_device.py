# Copyright 2020 The Cirq Developers
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
from typing import FrozenSet, Callable, List, Sequence
import numpy as np

import cirq
from cirq.ops import NamedQubit


@cirq.value.value_equality
class PasqalDevice(cirq.devices.Device):
    """A generic Pasqal device."""

    def __init__(self, qubits: Sequence[cirq.ops.Qid]) -> None:
        """Initializes a device with some qubits.

        Args:
            qubits (NamedQubit): Qubits on the device, exclusively unrelated to
                a physical position.
        Raises:
            TypeError: if the wrong qubit type is provided.
        """

        for q in qubits:
            if not isinstance(q, self.supported_qubit_type):
                raise TypeError('Unsupported qubit type: {!r}'.format(q))

        if len(qubits) > self.maximum_qubit_number:
            raise ValueError('Too many qubits. {} accepts at most {} '
                             'qubits.'.format(type(self),
                                              self.maximum_qubit_number))

        self.qubits = qubits

    @property
    def supported_qubit_type(self):
        return (NamedQubit,)

    @property
    def maximum_qubit_number(self):
        return 100

    def qubit_set(self) -> FrozenSet[cirq.Qid]:
        return frozenset(self.qubits)

    def qubit_list(self):
        return [qubit for qubit in self.qubits]

    def decompose_operation(self,
                            operation: cirq.ops.Operation) -> 'cirq.OP_TREE':

        decomposition = [operation]

        if not isinstance(operation,
                          (cirq.ops.GateOperation, cirq.ParallelGateOperation)):
            raise TypeError("{!r} is not a gate operation.".format(operation))

        # Try to decompose the operation into elementary device operations
        if not self.is_pasqal_device_op(operation):
            decomposition = PasqalConverter().pasqal_convert(
                operation, keep=self.is_pasqal_device_op)

        return decomposition

    def is_pasqal_device_op(self, op: cirq.ops.Operation) -> bool:

        if not isinstance(op, cirq.ops.Operation):
            raise ValueError('Got unknown operation:', op)

        valid_op = isinstance(op.gate,
                              (cirq.ops.IdentityGate, cirq.ops.MeasurementGate,
                               cirq.ops.PhasedXPowGate, cirq.ops.XPowGate,
                               cirq.ops.YPowGate, cirq.ops.ZPowGate))

        if not valid_op:  # To prevent further checking if already passed
            if isinstance(
                    op.gate,
                (cirq.ops.HPowGate, cirq.ops.CNotPowGate, cirq.ops.CZPowGate,
                 cirq.ops.CCZPowGate, cirq.ops.CCXPowGate)):
                expo = op.gate.exponent
                valid_op = np.isclose(expo, np.around(expo, decimals=0))

        return valid_op

    def validate_operation(self, operation: cirq.ops.Operation):
        """
        Raises an error if the given operation is invalid on this device.

        Args:
            operation: the operation to validate

        Raises:
            ValueError: If the operation is not valid
        """

        if not isinstance(operation,
                          (cirq.GateOperation, cirq.ParallelGateOperation)):
            raise ValueError("Unsupported operation")

        if not self.is_pasqal_device_op(operation):
            raise ValueError('{!r} is not a supported '
                             'gate'.format(operation.gate))

        for qub in operation.qubits:
            if not isinstance(qub, self.supported_qubit_type):
                raise ValueError('{} is not a valid qubit '
                                 'for gate {!r}'.format(qub, operation.gate))
            if qub not in self.qubit_set():
                raise ValueError('{} is not part of the device.'.format(qub))

        if isinstance(operation.gate, cirq.ops.MeasurementGate):
            if operation.gate.invert_mask != ():
                raise NotImplementedError("Measurements on Pasqal devices "
                                          "don't support invert_mask.")

    def validate_circuit(self, circuit: 'cirq.Circuit') -> None:
        """Raises an error if the given circuit is invalid on this device.

        A circuit is invalid if any of its moments are invalid or if there
        is a non-empty moment after a moment with a measurement.

        Args:
            circuit: The circuit to validate

        Raises:
            ValueError: If the given circuit can't be run on this device
        """
        super().validate_circuit(circuit)

        # Measurements must be in the last non-empty moment
        has_measurement_occurred = False
        for moment in circuit:
            if has_measurement_occurred:
                if len(moment.operations) > 0:
                    raise ValueError("Non-empty moment after measurement")
            for operation in moment.operations:
                if isinstance(operation.gate, cirq.ops.MeasurementGate):
                    has_measurement_occurred = True

    def __repr__(self):
        return 'pasqal.PasqalDevice(qubits={!r})'.format(sorted(self.qubits))

    def _value_equality_values_(self):
        return (self.qubits)

    def _json_dict_(self):
        return cirq.protocols.obj_to_dict_helper(self, ['qubits'])


class PasqalConverter(cirq.neutral_atoms.ConvertToNeutralAtomGates):
    """A gate converter for compatibility with Pasqal processors.

    Modified version of ConvertToNeutralAtomGates, where a new 'convert' method
    'pasqal_convert' takes the 'keep' function as an input.
    """

    def pasqal_convert(self, op: cirq.ops.Operation,
                       keep: Callable[[cirq.ops.Operation], bool]
                      ) -> List[cirq.ops.Operation]:

        def on_stuck_raise(bad):
            return TypeError("Don't know how to work with {!r}. "
                             "It isn't a native PasqalDevice operation, "
                             "a 1 or 2 qubit gate with a known unitary, "
                             "or composite.".format(bad))

        return cirq.protocols.decompose(
            op,
            keep=keep,
            intercepting_decomposer=self._convert_one,
            on_stuck_raise=None if self.ignore_failures else on_stuck_raise)
