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

from typing import Iterable, cast, Optional, List, TYPE_CHECKING

from cirq import ops, circuits
from cirq.devices import Device
from cirq.google import xmon_gates, convert_to_xmon_gates
from cirq.google.xmon_gate_extensions import xmon_gate_ext
from cirq.devices.grid_qubit import GridQubit
from cirq.value import Duration

from cirq.circuits import TextDiagramDrawer


if TYPE_CHECKING:
    # pylint: disable=unused-import
    from typing import Set


class XmonDevice(Device):
    """A device with qubits placed in a grid. Neighboring qubits can interact.
    """

    def __init__(self,
                 measurement_duration: Duration,
                 exp_w_duration: Duration,
                 exp_11_duration: Duration,
                 qubits: Iterable[GridQubit]) -> None:
        """Initializes the description of an xmon device.

        Args:
            measurement_duration: The maximum duration of a measurement.
            exp_w_duration: The maximum duration of an ExpW operation.
            exp_11_duration: The maximum duration of an ExpZ operation.
            qubits: Qubits on the device, identified by their x, y location.
        """
        self._measurement_duration = measurement_duration
        self._exp_w_duration = exp_w_duration
        self._exp_z_duration = exp_11_duration
        self.qubits = frozenset(qubits)

    def decompose_operation(self, operation: ops.Operation) -> ops.OP_TREE:
        return convert_to_xmon_gates.ConvertToXmonGates().convert(operation)

    def neighbors_of(self, qubit: GridQubit):
        """Returns the qubits that the given qubit can interact with."""
        possibles = [
            GridQubit(qubit.row + 1, qubit.col),
            GridQubit(qubit.row - 1, qubit.col),
            GridQubit(qubit.row, qubit.col + 1),
            GridQubit(qubit.row, qubit.col - 1),
        ]
        return [e for e in possibles if e in self.qubits]

    def duration_of(self, operation):
        if isinstance(operation, ops.GateOperation):
            g = xmon_gate_ext.try_cast(xmon_gates.XmonGate, operation.gate)
            if isinstance(g, xmon_gates.Exp11Gate):
                return self._exp_z_duration
            if isinstance(g, xmon_gates.ExpWGate):
                return self._exp_w_duration
            if isinstance(g, xmon_gates.XmonMeasurementGate):
                return self._measurement_duration
            if isinstance(g, xmon_gates.ExpZGate):
                # Z gates are performed in the control software.
                return Duration()
        raise ValueError('Unsupported gate type: {!r}'.format(operation))

    def validate_gate(self, gate: ops.Gate):
        """Raises an error if the given gate isn't allowed.

        Raises:
            ValueError: Unsupported gate.
        """
        if not isinstance(gate, (xmon_gates.Exp11Gate,
                                 xmon_gates.ExpWGate,
                                 xmon_gates.XmonMeasurementGate,
                                 xmon_gates.ExpZGate)):
            raise ValueError('Unsupported gate type: {!r}'.format(gate))

    def validate_operation(self, operation: ops.Operation):
        if not isinstance(operation, ops.GateOperation):
            raise ValueError('Unsupported operation: {!r}'.format(operation))

        self.validate_gate(operation.gate)

        for q in operation.qubits:
            if not isinstance(q, GridQubit):
                raise ValueError('Unsupported qubit type: {!r}'.format(q))
            if q not in self.qubits:
                raise ValueError('Qubit not on device: {!r}'.format(q))

        if (len(operation.qubits) == 2
                and not isinstance(operation.gate,
                                   xmon_gates.XmonMeasurementGate)):
            p, q = operation.qubits
            if not cast(GridQubit, p).is_adjacent(q):
                raise ValueError(
                    'Non-local interaction: {!r}.'.format(operation))

    def _check_if_exp11_operation_interacts_with_any(
            self,
            exp11_op: ops.GateOperation,
            others: Iterable[ops.GateOperation]) -> bool:
        return any(self._check_if_exp11_operation_interacts(exp11_op, op)
                   for op in others)

    def _check_if_exp11_operation_interacts(
            self,
            exp11_op: ops.GateOperation,
            other_op: ops.GateOperation) -> bool:
        if isinstance(other_op.gate, xmon_gates.ExpZGate):
            return False
        if isinstance(other_op.gate, xmon_gates.ExpWGate):
            return False
        if isinstance(other_op.gate, xmon_gates.XmonMeasurementGate):
            return False

        return any(cast(GridQubit, q).is_adjacent(cast(GridQubit, p))
                   for q in exp11_op.qubits
                   for p in other_op.qubits)

    def validate_scheduled_operation(self, schedule, scheduled_operation):
        self.validate_operation(scheduled_operation.operation)

        if isinstance(scheduled_operation.operation.gate,
                      xmon_gates.Exp11Gate):
            for other in schedule.operations_happening_at_same_time_as(
                    scheduled_operation):
                if self._check_if_exp11_operation_interacts(
                        cast(ops.GateOperation, scheduled_operation.operation),
                        cast(ops.GateOperation, other.operation)):
                    raise ValueError(
                        'Adjacent Exp11 operations: {} vs {}.'.format(
                            scheduled_operation, other))

    def validate_circuit(self, circuit: circuits.Circuit):
        super().validate_circuit(circuit)
        _verify_unique_measurement_keys(circuit.all_operations())

    def validate_moment(self, moment: circuits.Moment):
        super().validate_moment(moment)
        for op in moment.operations:
            if (isinstance(op, ops.GateOperation) and
                    isinstance(op.gate, xmon_gates.Exp11Gate)):
                for other in moment.operations:
                    if (other is not op and
                            self._check_if_exp11_operation_interacts(
                                cast(ops.GateOperation, op),
                                cast(ops.GateOperation, other))):
                        raise ValueError(
                            'Adjacent Exp11 operations: {}.'.format(moment))

    def can_add_operation_into_moment(self,
                                      operation: ops.Operation,
                                      moment: circuits.Moment) -> bool:
        self.validate_moment(moment)

        if not super().can_add_operation_into_moment(operation, moment):
            return False
        if (isinstance(operation, ops.GateOperation) and
                isinstance(operation.gate, xmon_gates.Exp11Gate)):
            return not self._check_if_exp11_operation_interacts_with_any(
                cast(ops.GateOperation, operation),
                cast(Iterable[ops.GateOperation], moment.operations))
        return True

    def validate_schedule(self, schedule):
        _verify_unique_measurement_keys(
            s.operation for s in schedule.scheduled_operations)
        for scheduled_operation in schedule.scheduled_operations:
            self.validate_scheduled_operation(schedule, scheduled_operation)

    def at(self, row: int, col: int) -> Optional[GridQubit]:
        """Returns the qubit at the given position, if there is one, else None.
        """
        q = GridQubit(row, col)
        return q if q in self.qubits else None

    def row(self, row: int) -> List[GridQubit]:
        """Returns the qubits in the given row, in ascending order."""
        return sorted(q for q in self.qubits if q.row == row)

    def col(self, col: int) -> List[GridQubit]:
        """Returns the qubits in the given column, in ascending order."""
        return sorted(q for q in self.qubits if q.col == col)

    def __repr__(self):
        return ('XmonDevice(measurement_duration={!r}, '
                'exp_w_duration={!r}, '
                'exp_11_duration={!r} '
                'qubits={!r})').format(self._measurement_duration,
                                       self._exp_w_duration,
                                       self._exp_z_duration,
                                       sorted(self.qubits))

    def __str__(self):
        diagram = TextDiagramDrawer()

        for q in self.qubits:
            diagram.write(q.col, q.row, str(q))
            for q2 in self.neighbors_of(q):
                diagram.grid_line(q.col, q.row, q2.col, q2.row)

        return diagram.render(
            horizontal_spacing=3,
            vertical_spacing=2,
            use_unicode_characters=True)

    def __eq__(self, other):
        if not isinstance(other, (XmonDevice, type(self))):
            return NotImplemented
        return (self._measurement_duration == other._measurement_duration and
                self._exp_w_duration == other._exp_w_duration and
                self._exp_z_duration == other._exp_z_duration and
                self.qubits == other.qubits)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((XmonDevice, self._measurement_duration,
                     self._exp_w_duration, self._exp_z_duration, self.qubits))


def _verify_unique_measurement_keys(operations: Iterable[ops.Operation]):
    seen = set()  # type: Set[str]
    for op in operations:
        if ops.MeasurementGate.is_measurement(op):
            key = cast(ops.MeasurementGate,
                       cast(ops.GateOperation, op).gate).key
            if key in seen:
                raise ValueError('Measurement key {} repeated'.format(key))
            seen.add(key)
