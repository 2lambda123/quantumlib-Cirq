# Copyright 2019 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable, Optional, Union, Iterable, List, Sequence, Iterator

import numpy as np

import cirq
from cirq import ops, linalg
from cirq.contrib.quirk.cells.cell import Cell, CellMaker


class InputRotationCell(Cell):
    """Applies an operation that depends on an input gate."""

    def __init__(self, identifier: str,
                 register: Optional[Sequence['cirq.Qid']],
                 base_operation: 'cirq.Operation', exponent_sign: int):
        self.identifier = identifier
        self.register = None if register is None else tuple(register)
        self.base_operation = base_operation
        self.exponent_sign = exponent_sign

    def with_input(self, letter, register):
        if self.register is None and letter == 'a':
            if isinstance(register, int):
                raise ValueError('Dependent operation requires known length '
                                 'input; classical constant not allowed.')
            return InputRotationCell(self.identifier, register,
                                     self.base_operation, self.exponent_sign)
        return self

    def controlled_by(self, qubit: 'cirq.Qid'):
        return InputRotationCell(self.identifier, self.register,
                                 self.base_operation.controlled_by(qubit),
                                 self.exponent_sign)

    def operations(self) -> 'cirq.OP_TREE':
        if self.register is None:
            raise ValueError(f"Missing input 'a'")
        return QuirkInputRotationOperation(self.identifier, self.register,
                                           self.base_operation,
                                           self.exponent_sign)


class QuirkInputRotationOperation(ops.Operation):
    """Operates on target qubits in a way that varies based on an input qureg.
    """

    def __init__(self, identifier: str, register: Iterable['cirq.Qid'],
                 base_operation: 'cirq.Operation', exponent_sign: int):
        self.identifier = identifier
        self.register = tuple(register)
        self.base_operation = base_operation
        self.exponent_sign = exponent_sign

    @property
    def qubits(self):
        return tuple(self.base_operation.qubits) + self.register

    def with_qubits(self, *new_qubits):
        new_op_qubits = new_qubits[:len(self.base_operation.qubits)]
        new_register = new_qubits[len(self.base_operation.qubits):]
        return QuirkInputRotationOperation(self.identifier, new_register,
                                           self.base_operation,
                                           self.exponent_sign)

    def _circuit_diagram_info_(self, args: 'cirq.CircuitDiagramInfoArgs'):
        sub_result = cirq.circuit_diagram_info(self.base_operation)
        sign_char = '-' if self.exponent_sign == -1 else ''
        symbols = list(sub_result.wire_symbols)
        symbols.extend(f'A{i}' for i in range(len(self.register)))
        qubit_index = (len(self.base_operation.controls) if isinstance(
            self.base_operation, ops.ControlledOperation) else 0)
        return cirq.CircuitDiagramInfo(
            tuple(symbols),
            exponent=f'({sign_char}A/2^{len(self.register)})',
            exponent_qubit_index=qubit_index,
            auto_exponent_parens=False)

    def _has_unitary_(self):
        return True

    def _apply_unitary_(self, args: 'cirq.ApplyUnitaryArgs'):
        transposed_args = args.with_axes_transposed_to_start()

        target_axes = transposed_args.axes[:len(self.base_operation.qubits)]
        control_axes = transposed_args.axes[len(self.base_operation.qubits):]
        control_max = np.product([q.dimension for q in self.register]).item()

        for i in range(control_max):
            operation = self.base_operation**(self.exponent_sign * i /
                                              control_max)
            control_index = linalg.slice_for_qubits_equal_to(
                control_axes, big_endian_qureg_value=i)
            sub_args = cirq.ApplyUnitaryArgs(
                transposed_args.target_tensor[control_index],
                transposed_args.available_buffer[control_index], target_axes)
            sub_result = cirq.apply_unitary(operation, sub_args)

            if sub_result is not sub_args.target_tensor:
                sub_args.target_tensor[...] = sub_result

        return args.target_tensor


def generate_all_input_rotation_cell_makers() -> Iterator[CellMaker]:
    yield _input_rotation_gate("X^(A/2^n)", ops.X, +1)
    yield _input_rotation_gate("Y^(A/2^n)", ops.Y, +1)
    yield _input_rotation_gate("Z^(A/2^n)", ops.Z, +1)
    yield _input_rotation_gate("X^(-A/2^n)", ops.X, -1)
    yield _input_rotation_gate("Y^(-A/2^n)", ops.Y, -1)
    yield _input_rotation_gate("Z^(-A/2^n)", ops.Z, -1)


def _input_rotation_gate(identifier: str, gate: 'cirq.Gate',
                         factor: int) -> CellMaker:
    return CellMaker(
        identifier, gate.num_qubits(), lambda args: InputRotationCell(
            identifier=identifier,
            register=None,
            base_operation=gate.on(args.qubits[0]),
            exponent_sign=factor))
