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

"""Quantum gates that are commonly used in the literature.

This module creates Gate instances for the following gates:
    X,Y,Z: Pauli gates.
    H,S: Clifford gates.
    T: A non-Clifford gate.
    CZ: Controlled phase gate.
    CNOT: Controlled not gate.

Each of these are implemented as EigenGates, which means that they can be
raised to a power (i.e. cirq.H**0.5). See the definition in EigenGate.
"""
import warnings
from typing import Any, cast, Iterable, List, Optional, Tuple, Union

import numpy as np
import sympy

import cirq
from cirq import protocols, value
from cirq._compat import proper_repr
from cirq.ops import gate_features, eigen_gate, raw_types

from cirq.type_workarounds import NotImplementedType

from cirq.ops.swap_gates import ISWAP, SWAP, ISwapPowGate, SwapPowGate
from cirq.ops.measurement_gate import MeasurementGate

assert all([ISWAP, SWAP, ISwapPowGate, SwapPowGate, MeasurementGate]), """
Included for compatibility. Please continue to use top-level cirq.{thing}
imports.
"""


@value.value_equality
class XPowGate(eigen_gate.EigenGate,
               gate_features.SingleQubitGate):
    """A gate that rotates around the X axis of the Bloch sphere.

    The unitary matrix of ``XPowGate(exponent=t)`` is:

        [[g·c, -i·g·s],
         [-i·g·s, g·c]]

    where:

        c = cos(π·t/2)
        s = sin(π·t/2)
        g = exp(i·π·t/2).

    Note in particular that this gate has a global phase factor of
    e^{i·π·t/2} vs the traditionally defined rotation matrices
    about the Pauli X axis. See `cirq.Rx` for rotations without the global
    phase. The global phase factor can be adjusted by using the `global_shift`
    parameter when initializing.

    `cirq.X`, the Pauli X gate, is an instance of this gate at exponent=1.
    """

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Optional[np.ndarray]:
        if self._exponent != 1:
            return NotImplemented
        zero = args.subspace_index(0)
        one = args.subspace_index(1)
        args.available_buffer[zero] = args.target_tensor[one]
        args.available_buffer[one] = args.target_tensor[zero]
        p = 1j**(2 * self._exponent * self._global_shift)
        if p != 1:
            args.available_buffer *= p
        return args.available_buffer

    def in_su2(self) -> 'XPowGate':
        """Returns an equal-up-global-phase gate from the group SU2."""
        return XPowGate(exponent=self._exponent, global_shift=-0.5)

    def with_canonical_global_phase(self) -> 'XPowGate':
        """Returns an equal-up-global-phase standardized form of the gate."""
        return XPowGate(exponent=self._exponent)

    def _eigen_components(self):
        return [
            (0, np.array([[0.5, 0.5], [0.5, 0.5]])),
            (1, np.array([[0.5, -0.5], [-0.5, 0.5]])),
        ]

    def _trace_distance_bound_(self) -> Optional[float]:
        if self._is_parameterized_():
            return None
        return abs(np.sin(self._exponent * 0.5 * np.pi))

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if protocols.is_parameterized(self):
            return NotImplemented
        phase = 1j**(2 * self._exponent * (self._global_shift + 0.5))
        angle = np.pi * self._exponent / 2
        return value.LinearDict({
            'I': phase * np.cos(angle),
            'X': -1j * phase * np.sin(angle),
        })

    def _circuit_diagram_info_(self, args: 'protocols.CircuitDiagramInfoArgs'
                              ) -> Union[str, 'protocols.CircuitDiagramInfo']:
        if self._global_shift == -0.5:
            return _rads_func_symbol(
                'Rx',
                args,
                self._diagram_exponent(args, ignore_global_phase=False))

        return protocols.CircuitDiagramInfo(
            wire_symbols=('X',),
            exponent=self._diagram_exponent(args))

    def _qasm_(self, args: 'protocols.QasmArgs',
               qubits: Tuple[raw_types.Qid, ...]) -> Optional[str]:
        args.validate_version('2.0')
        if self._exponent == 1:
            return args.format('x {0};\n', qubits[0])

        return args.format('rx({0:half_turns}) {1};\n', self._exponent,
                           qubits[0])

    @property
    def phase_exponent(self):
        return 0.0

    def _phase_by_(self, phase_turns, qubit_index):
        """See `cirq.SupportsPhase`."""
        return cirq.ops.phased_x_gate.PhasedXPowGate(
            exponent=self._exponent,
            phase_exponent=phase_turns * 2)

    def __str__(self) -> str:
        if self._global_shift == -0.5:
            if self._exponent == 1:
                return 'Rx(π)'
            return 'Rx({}π)'.format(self._exponent)
        if self._global_shift == 0:
            if self._exponent == 1:
                return 'X'
            return 'X**{}'.format(self._exponent)
        return ('XPowGate(exponent={}, '
                'global_shift={!r})').format(self._exponent, self._global_shift)

    def __repr__(self) -> str:
        if self._global_shift == -0.5:
            if protocols.is_parameterized(self._exponent):
                return 'cirq.Rx({})'.format(
                    proper_repr(sympy.pi * self._exponent))

            return 'cirq.Rx(np.pi*{})'.format(proper_repr(self._exponent))
        if self._global_shift == 0:
            if self._exponent == 1:
                return 'cirq.X'
            return '(cirq.X**{})'.format(proper_repr(self._exponent))
        return (
            'cirq.XPowGate(exponent={}, '
            'global_shift={!r})'
        ).format(proper_repr(self._exponent), self._global_shift)


@value.value_equality
class YPowGate(eigen_gate.EigenGate,
               gate_features.SingleQubitGate):
    """A gate that rotates around the Y axis of the Bloch sphere.

    The unitary matrix of ``YPowGate(exponent=t)`` is:

        [[g·c, -g·s],
         [g·s, g·c]]

    where:

        c = cos(π·t/2)
        s = sin(π·t/2)
        g = exp(i·π·t/2).

    Note in particular that this gate has a global phase factor of
    e^{i·π·t/2} vs the traditionally defined rotation matrices
    about the Pauli Y axis. See `cirq.Ry` for rotations without the global
    phase. The global phase factor can be adjusted by using the `global_shift`
    parameter when initializing.

    `cirq.Y`, the Pauli Y gate, is an instance of this gate at exponent=1.
    """

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Optional[np.ndarray]:
        if self._exponent != 1:
            return NotImplemented
        zero = args.subspace_index(0)
        one = args.subspace_index(1)
        args.available_buffer[zero] = -1j * args.target_tensor[one]
        args.available_buffer[one] = 1j * args.target_tensor[zero]
        p = 1j**(2 * self._exponent * self._global_shift)
        if p != 1:
            args.available_buffer *= p
        return args.available_buffer

    def in_su2(self) -> 'YPowGate':
        """Returns an equal-up-global-phase gate from the group SU2."""
        return YPowGate(exponent=self._exponent, global_shift=-0.5)

    def with_canonical_global_phase(self) -> 'YPowGate':
        """Returns an equal-up-global-phase standardized form of the gate."""
        return YPowGate(exponent=self._exponent)

    def _eigen_components(self):
        return [
            (0, np.array([[0.5, -0.5j], [0.5j, 0.5]])),
            (1, np.array([[0.5, 0.5j], [-0.5j, 0.5]])),
        ]

    def _trace_distance_bound_(self) -> Optional[float]:
        if self._is_parameterized_():
            return None
        return abs(np.sin(self._exponent * 0.5 * np.pi))

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if protocols.is_parameterized(self):
            return NotImplemented
        phase = 1j**(2 * self._exponent * (self._global_shift + 0.5))
        angle = np.pi * self._exponent / 2
        return value.LinearDict({
            'I': phase * np.cos(angle),
            'Y': -1j * phase * np.sin(angle),
        })

    def _circuit_diagram_info_(self, args: 'protocols.CircuitDiagramInfoArgs'
                              ) -> Union[str, 'protocols.CircuitDiagramInfo']:
        if self._global_shift == -0.5:
            return _rads_func_symbol(
                'Ry',
                args,
                self._diagram_exponent(args, ignore_global_phase=False))

        return protocols.CircuitDiagramInfo(
            wire_symbols=('Y',),
            exponent=self._diagram_exponent(args))

    def _qasm_(self, args: 'protocols.QasmArgs',
               qubits: Tuple[raw_types.Qid, ...]) -> Optional[str]:
        args.validate_version('2.0')
        if self._exponent == 1:
            return args.format('y {0};\n', qubits[0])

        return args.format('ry({0:half_turns}) {1};\n', self._exponent,
                           qubits[0])

    @property
    def phase_exponent(self):
        return 0.5

    def _phase_by_(self, phase_turns, qubit_index):
        """See `cirq.SupportsPhase`."""
        return cirq.ops.phased_x_gate.PhasedXPowGate(
            exponent=self._exponent,
            phase_exponent=0.5 + phase_turns * 2)

    def __str__(self) -> str:
        if self._global_shift == -0.5:
            if self._exponent == 1:
                return 'Ry(π)'
            return 'Ry({}π)'.format(self._exponent)
        if self._global_shift == 0:
            if self._exponent == 1:
                return 'Y'
            return 'Y**{}'.format(self._exponent)
        return ('YPowGate(exponent={}, '
                'global_shift={!r})').format(self._exponent, self._global_shift)

    def __repr__(self) -> str:
        if self._global_shift == -0.5:
            if protocols.is_parameterized(self._exponent):
                return 'cirq.Ry({})'.format(
                    proper_repr(sympy.pi * self._exponent))

            return 'cirq.Ry(np.pi*{})'.format(proper_repr(self._exponent))
        if self._global_shift == 0:
            if self._exponent == 1:
                return 'cirq.Y'
            return '(cirq.Y**{})'.format(proper_repr(self._exponent))
        return (
            'cirq.YPowGate(exponent={}, '
            'global_shift={!r})'
        ).format(proper_repr(self._exponent), self._global_shift)


@value.value_equality
class ZPowGate(eigen_gate.EigenGate,
               gate_features.SingleQubitGate):
    """A gate that rotates around the Z axis of the Bloch sphere.

    The unitary matrix of ``ZPowGate(exponent=t)`` is:

        [[1, 0],
         [0, g]]

    where:

        g = exp(i·π·t).

    Note in particular that this gate has a global phase factor of
    e^{i·π·t/2} vs the traditionally defined rotation matrices
    about the Pauli Z axis. See `cirq.Rz` for rotations without the global
    phase. The global phase factor can be adjusted by using the `global_shift`
    parameter when initializing.

    `cirq.Z`, the Pauli Z gate, is an instance of this gate at exponent=1.
    """

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Optional[np.ndarray]:
        if protocols.is_parameterized(self):
            return None

        one = args.subspace_index(1)
        c = 1j**(self._exponent * 2)
        args.target_tensor[one] *= c
        p = 1j**(2 * self._exponent * self._global_shift)
        if p != 1:
            args.target_tensor *= p
        return args.target_tensor

    def in_su2(self) -> 'ZPowGate':
        """Returns an equal-up-global-phase gate from the group SU2."""
        return ZPowGate(exponent=self._exponent, global_shift=-0.5)

    def with_canonical_global_phase(self) -> 'ZPowGate':
        """Returns an equal-up-global-phase standardized form of the gate."""
        return ZPowGate(exponent=self._exponent)

    def _eigen_components(self):
        return [
            (0, np.diag([1, 0])),
            (1, np.diag([0, 1])),
        ]

    def _trace_distance_bound_(self) -> Optional[float]:
        if self._is_parameterized_():
            return None
        return abs(np.sin(self._exponent * 0.5 * np.pi))

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if protocols.is_parameterized(self):
            return NotImplemented
        phase = 1j**(2 * self._exponent * (self._global_shift + 0.5))
        angle = np.pi * self._exponent / 2
        return value.LinearDict({
            'I': phase * np.cos(angle),
            'Z': -1j * phase * np.sin(angle),
        })

    def _phase_by_(self, phase_turns: float, qubit_index: int):
        return self

    def _circuit_diagram_info_(self, args: 'protocols.CircuitDiagramInfoArgs'
                              ) -> Union[str, 'protocols.CircuitDiagramInfo']:
        if self._global_shift == -0.5:
            return _rads_func_symbol(
                'Rz',
                args,
                self._diagram_exponent(args, ignore_global_phase=False))

        e = self._diagram_exponent(args)
        if e in [-0.25, 0.25]:
            return protocols.CircuitDiagramInfo(
                wire_symbols=('T',),
                exponent=cast(float, e) * 4)

        if e in [-0.5, 0.5]:
            return protocols.CircuitDiagramInfo(
                wire_symbols=('S',),
                exponent=cast(float, e) * 2)

        return protocols.CircuitDiagramInfo(
            wire_symbols=('Z',),
            exponent=e)

    def _qasm_(self, args: 'protocols.QasmArgs',
               qubits: Tuple[raw_types.Qid, ...]) -> Optional[str]:
        args.validate_version('2.0')
        if self._exponent == 1:
            return args.format('z {0};\n', qubits[0])

        return args.format('rz({0:half_turns}) {1};\n', self._exponent,
                           qubits[0])

    def __str__(self) -> str:
        if self._global_shift == -0.5:
            if self._exponent == 1:
                return 'Rz(π)'
            return 'Rz({}π)'.format(self._exponent)
        if self._global_shift == 0:
            if self._exponent == 0.25:
                return 'T'
            if self._exponent == -0.25:
                return 'T**-1'
            if self._exponent == 0.5:
                return 'S'
            if self._exponent == -0.5:
                return 'S**-1'
            if self._exponent == 1:
                return 'Z'
            return 'Z**{}'.format(self._exponent)
        return ('ZPowGate(exponent={}, '
                'global_shift={!r})').format(self._exponent, self._global_shift)

    def __repr__(self) -> str:
        if self._global_shift == -0.5:
            if protocols.is_parameterized(self._exponent):
                return 'cirq.Rz({})'.format(proper_repr(
                    sympy.pi * self._exponent))

            return 'cirq.Rz(np.pi*{!r})'.format(self._exponent)
        if self._global_shift == 0:
            if self._exponent == 0.25:
                return 'cirq.T'
            if self._exponent == -0.25:
                return '(cirq.T**-1)'
            if self._exponent == 0.5:
                return 'cirq.S'
            if self._exponent == -0.5:
                return '(cirq.S**-1)'
            if self._exponent == 1:
                return 'cirq.Z'
            return '(cirq.Z**{})'.format(proper_repr(self._exponent))
        return (
            'cirq.ZPowGate(exponent={}, '
            'global_shift={!r})'
        ).format(proper_repr(self._exponent), self._global_shift)


@value.value_equality
class IdentityGate(raw_types.Gate):
    """A Gate that perform no operation on qubits.

    The unitary matrix of this gate is a diagonal matrix with all 1s on the
    diagonal and all 0s off the diagonal in any basis.

    `cirq.I` is the single qubit identity gate.
    """

    def __init__(self,
                 num_qubits: Optional[int] = None,
                 qid_shape: Tuple[int, ...] = None):
        """
        Args:
            num_qubits:
            qid_shape: Specifies the dimension of each qid the measurement
                applies to.  The default is 2 for every qubit.

        Raises:
            ValueError: If the length of qid_shape doesn't equal num_qubits.
        """
        if qid_shape is None:
            if num_qubits is None:
                raise ValueError(
                    'Specify either the num_qubits or qid_shape argument.')
            qid_shape = (2,) * num_qubits
        elif num_qubits is None:
            num_qubits = len(qid_shape)
        self._qid_shape = qid_shape
        if len(self._qid_shape) != num_qubits:
            raise ValueError('len(qid_shape) != num_qubits')

    def _qid_shape_(self) -> Tuple[int, ...]:
        return self._qid_shape

    def on_each(self, *targets: Union[raw_types.Qid, Iterable[Any]]
               ) -> List[raw_types.Operation]:
        """Returns a list of operations that applies the single qubit identity
        to each of the targets.

        Args:
            *targets: The qubits to apply this gate to.

        Returns:
            Operations applying this gate to the target qubits.

        Raises:
            ValueError if targets are not instances of Qid or List[Qid] or
            the gate from which this is applied is not a single qubit identity
            gate.
        """
        if len(self._qid_shape) != 1:
            raise ValueError(
                'IdentityGate only supports on_each when it is a one qubit '
                'gate.')
        operations: List[raw_types.Operation] = []
        for target in targets:
            if isinstance(target, Iterable) and not isinstance(target, str):
                operations.extend(self.on_each(*target))
            elif isinstance(target, raw_types.Qid):
                operations.append(self.on(target))
            else:
                raise ValueError(
                    'Gate was called with type different than Qid. Type: {}'.
                    format(type(target)))
        return operations

    def _unitary_(self):
        return np.identity(np.prod(self._qid_shape, dtype=int))

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Optional[np.ndarray]:
        return args.target_tensor

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if not all(d == 2 for d in self._qid_shape):
            return NotImplemented
        return value.LinearDict({'I' * self.num_qubits(): 1.0})

    def _trace_distance_bound_(self) -> float:
        return 0.0

    def __repr__(self):
        if self._qid_shape == (2,):
            return 'cirq.I'
        other = ''
        if not all(d == 2 for d in self._qid_shape):
            other = ', {!r}'.format(self._qid_shape)
        return 'cirq.IdentityGate({!r}{})'.format(self.num_qubits(), other)

    def __str__(self):
        if (self.num_qubits() == 1):
            return 'I'

        return 'I({})'.format(self.num_qubits())

    def _circuit_diagram_info_(self, args: 'protocols.CircuitDiagramInfoArgs'
                              ) -> 'protocols.CircuitDiagramInfo':
        return protocols.CircuitDiagramInfo(
            wire_symbols=('I',) * self.num_qubits(), connected=True)

    def _qasm_(self, args: 'protocols.QasmArgs',
               qubits: Tuple[raw_types.Qid, ...]) -> Optional[str]:
        if not all(d == 2 for d in self._qid_shape):
            return NotImplemented
        args.validate_version('2.0')
        return ''.join([args.format('id {0};\n', qubit) for qubit in qubits])

    def _value_equality_values_(self):
        return self._qid_shape

    def _json_dict_(self):
        other = {}
        if not all(d == 2 for d in self._qid_shape):
            other['qid_shape'] = self._qid_shape
        return {
            'cirq_type': self.__class__.__name__,
            'num_qubits': len(self._qid_shape),
            **other,
        }

    @classmethod
    def _from_json_dict_(cls, num_qubits, qid_shape=None, **kwargs):
        return cls(num_qubits=num_qubits,
                   qid_shape=None if qid_shape is None else tuple(qid_shape))


def identity(*qubits: raw_types.Qid) -> raw_types.Operation:
    """Returns a single IdentityGate applied to all the given qubits.

    Args:
        *qubits: The qubits that the identity gate will apply to.

    Returns:
        An identity operation on the given qubits.

    Raises:
        ValueError if the qubits are not instances of Qid.
    """
    if not all(isinstance(qubit, raw_types.Qid) for qubit in qubits):
        raise ValueError('identity() was called with type different than Qid.')

    qid_shape = protocols.qid_shape(qubits)
    return IdentityGate(len(qubits), qid_shape).on(*qubits)


class HPowGate(eigen_gate.EigenGate, gate_features.SingleQubitGate):
    """A Gate that performs a rotation around the X+Z axis of the Bloch sphere.

    The unitary matrix of ``HPowGate(exponent=t)`` is:

        [[g·(c-i·s/sqrt(2)), -i·g·s/sqrt(2)],
        [-i·g·s/sqrt(2)], g·(c+i·s/sqrt(2))]]

    where

        c = cos(π·t/2)
        s = sin(π·t/2)
        g = exp(i·π·t/2).

    Note in particular that for `t=1`, this gives the Hadamard matrix.

    `cirq.H`, the Hadamard gate, is an instance of this gate at `exponent=1`.
    """

    def _eigen_components(self):
        s = np.sqrt(2)

        component0 = np.array([
            [3 + 2 * s, 1 + s],
            [1 + s, 1]
        ]) / (4 + 2 * s)

        component1 = np.array([
            [3 - 2 * s, 1 - s],
            [1 - s, 1]
        ]) / (4 - 2 * s)

        return [(0, component0), (1, component1)]

    def _trace_distance_bound_(self) -> Optional[float]:
        if self._is_parameterized_():
            return None
        return abs(np.sin(self._exponent * 0.5 * np.pi))

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if protocols.is_parameterized(self):
            return NotImplemented
        phase = 1j**(2 * self._exponent * (self._global_shift + 0.5))
        angle = np.pi * self._exponent / 2
        return value.LinearDict({
            'I': phase * np.cos(angle),
            'X': -1j * phase * np.sin(angle) / np.sqrt(2),
            'Z': -1j * phase * np.sin(angle) / np.sqrt(2),
        })

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Optional[np.ndarray]:
        if self._exponent != 1:
            return NotImplemented

        zero = args.subspace_index(0)
        one = args.subspace_index(1)
        args.target_tensor[one] -= args.target_tensor[zero]
        args.target_tensor[one] *= -0.5
        args.target_tensor[zero] -= args.target_tensor[one]
        p = 1j**(2 * self._exponent * self._global_shift)
        args.target_tensor *= np.sqrt(2) * p
        return args.target_tensor

    def _decompose_(self, qubits):
        q = qubits[0]

        if self._exponent == 1:
            yield cirq.Y(q)**0.5
            yield cirq.XPowGate(global_shift=-0.25).on(q)
            return

        yield YPowGate(exponent=0.25).on(q)
        yield XPowGate(exponent=self._exponent).on(q)
        yield YPowGate(exponent=-0.25).on(q)

    def _circuit_diagram_info_(self, args: 'protocols.CircuitDiagramInfoArgs'
                              ) -> 'protocols.CircuitDiagramInfo':
        return protocols.CircuitDiagramInfo(
            wire_symbols=('H',),
            exponent=self._diagram_exponent(args))

    def _qasm_(self, args: 'protocols.QasmArgs',
               qubits: Tuple[raw_types.Qid, ...]) -> Optional[str]:
        args.validate_version('2.0')
        if self._exponent == 1:
            return args.format('h {0};\n', qubits[0])

        return args.format(
            'ry({0:half_turns}) {3};\n'
            'rx({1:half_turns}) {3};\n'
            'ry({2:half_turns}) {3};\n', 0.25, self._exponent, -0.25, qubits[0])

    def __str__(self):
        if self._exponent == 1:
            return 'H'
        return 'H^{}'.format(self._exponent)

    def __repr__(self):
        if self._global_shift == 0:
            if self._exponent == 1:
                return 'cirq.H'
            return '(cirq.H**{})'.format(proper_repr(self._exponent))
        return (
            'cirq.HPowGate(exponent={}, '
            'global_shift={!r})'
        ).format(proper_repr(self._exponent), self._global_shift)


class CZPowGate(eigen_gate.EigenGate,
                gate_features.TwoQubitGate,
                gate_features.InterchangeableQubitsGate):
    """A gate that applies a phase to the |11⟩ state of two qubits.

    The unitary matrix of `CZPowGate(exponent=t)` is:

        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, g]]

    where:

        g = exp(i·π·t).

    `cirq.CZ`, the controlled Z gate, is an instance of this gate at
    `exponent=1`.
    """

    def _eigen_components(self):
        return [
            (0, np.diag([1, 1, 1, 0])),
            (1, np.diag([0, 0, 0, 1])),
        ]

    def _trace_distance_bound_(self) -> Optional[float]:
        if self._is_parameterized_():
            return None
        return abs(np.sin(self._exponent * 0.5 * np.pi))

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Union[np.ndarray, NotImplementedType]:
        if protocols.is_parameterized(self):
            return NotImplemented

        c = 1j**(2 * self._exponent)
        one_one = args.subspace_index(0b11)
        args.target_tensor[one_one] *= c
        p = 1j**(2 * self._exponent * self._global_shift)
        if p != 1:
            args.target_tensor *= p
        return args.target_tensor

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if protocols.is_parameterized(self):
            return NotImplemented
        global_phase = 1j**(2 * self._exponent * self._global_shift)
        z_phase = 1j**self._exponent
        c = -1j * z_phase * np.sin(np.pi * self._exponent / 2) / 2
        return value.LinearDict({
            'II': global_phase * (1 - c),
            'IZ': global_phase * c,
            'ZI': global_phase * c,
            'ZZ': global_phase * -c,
        })

    def _phase_by_(self, phase_turns, qubit_index):
        return self

    def _circuit_diagram_info_(self, args: 'protocols.CircuitDiagramInfoArgs'
                              ) -> 'protocols.CircuitDiagramInfo':
        return protocols.CircuitDiagramInfo(
                wire_symbols=('@', '@'),
                exponent=self._diagram_exponent(args))

    def _qasm_(self, args: 'protocols.QasmArgs',
               qubits: Tuple[raw_types.Qid, ...]) -> Optional[str]:
        if self._exponent != 1:
            return None  # Don't have an equivalent gate in QASM
        args.validate_version('2.0')
        return args.format('cz {0},{1};\n', qubits[0], qubits[1])

    def __str__(self) -> str:
        if self._exponent == 1:
            return 'CZ'
        return 'CZ**{!r}'.format(self._exponent)

    def __repr__(self) -> str:
        if self._global_shift == 0:
            if self._exponent == 1:
                return 'cirq.CZ'
            return '(cirq.CZ**{})'.format(proper_repr(self._exponent))
        return (
            'cirq.CZPowGate(exponent={}, '
            'global_shift={!r})'
        ).format(proper_repr(self._exponent), self._global_shift)


def _rads_func_symbol(func_name: str, args: 'protocols.CircuitDiagramInfoArgs',
                      half_turns: Any) -> str:
    if protocols.is_parameterized(half_turns):
        return '{}({})'.format(func_name, sympy.pi * half_turns)
    unit = 'π' if args.use_unicode_characters else 'pi'
    if half_turns == 1:
        return '{}({})'.format(func_name, unit)
    if half_turns == -1:
        return '{}(-{})'.format(func_name, unit)
    return '{}({}{})'.format(func_name, half_turns, unit)


class CNotPowGate(eigen_gate.EigenGate, gate_features.TwoQubitGate):
    """A gate that applies a controlled power of an X gate.

    When applying CNOT (controlled-not) to qubits, you can either use
    positional arguments CNOT(q1, q2), where q2 is toggled when q1 is on,
    or named arguments CNOT(control=q1, target=q2).
    (Mixing the two is not permitted.)

    The unitary matrix of `CNotPowGate(exponent=t)` is:

        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, g·c, -i·g·s],
         [0, 0, -i·g·s, g·c]]

    where:

        c = cos(π·t/2)
        s = sin(π·t/2)
        g = exp(i·π·t/2).

    `cirq.CNOT`, the controlled NOT gate, is an instance of this gate at
    `exponent=1`.
    """

    def _decompose_(self, qubits):
        c, t = qubits
        yield YPowGate(exponent=-0.5).on(t)
        yield CZ(c, t)**self._exponent
        yield YPowGate(exponent=0.5).on(t)

    def _eigen_components(self):
        return [
            (0, np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 0.5, 0.5],
                          [0, 0, 0.5, 0.5]])),
            (1, np.array([[0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0.5, -0.5],
                          [0, 0, -0.5, 0.5]])),
        ]

    def _trace_distance_bound_(self) -> Optional[float]:
        if self._is_parameterized_():
            return None
        return abs(np.sin(self._exponent * 0.5 * np.pi))

    def _circuit_diagram_info_(self, args: 'protocols.CircuitDiagramInfoArgs'
                              ) -> 'protocols.CircuitDiagramInfo':
        return protocols.CircuitDiagramInfo(
            wire_symbols=('@', 'X'),
            exponent=self._diagram_exponent(args))

    def _apply_unitary_(self, args: 'protocols.ApplyUnitaryArgs'
                       ) -> Optional[np.ndarray]:
        if self._exponent != 1:
            return NotImplemented

        oo = args.subspace_index(0b11)
        zo = args.subspace_index(0b01)
        args.available_buffer[oo] = args.target_tensor[oo]
        args.target_tensor[oo] = args.target_tensor[zo]
        args.target_tensor[zo] = args.available_buffer[oo]
        p = 1j**(2 * self._exponent * self._global_shift)
        if p != 1:
            args.target_tensor *= p
        return args.target_tensor

    def _pauli_expansion_(self) -> value.LinearDict[str]:
        if protocols.is_parameterized(self):
            return NotImplemented
        global_phase = 1j**(2 * self._exponent * self._global_shift)
        cnot_phase = 1j**self._exponent
        c = -1j * cnot_phase * np.sin(np.pi * self._exponent / 2) / 2
        return value.LinearDict({
            'II': global_phase * (1 - c),
            'IX': global_phase * c,
            'ZI': global_phase * c,
            'ZX': global_phase * -c,
        })

    def _qasm_(self, args: 'protocols.QasmArgs',
               qubits: Tuple[raw_types.Qid, ...]) -> Optional[str]:
        if self._exponent != 1:
            return None  # Don't have an equivalent gate in QASM
        args.validate_version('2.0')
        return args.format('cx {0},{1};\n', qubits[0], qubits[1])

    def __str__(self) -> str:
        if self._exponent == 1:
            return 'CNOT'
        return 'CNOT**{!r}'.format(self._exponent)

    def __repr__(self):
        if self._global_shift == 0:
            if self._exponent == 1:
                return 'cirq.CNOT'
            return '(cirq.CNOT**{})'.format(proper_repr(self._exponent))
        return (
            'cirq.CNotPowGate(exponent={}, '
            'global_shift={!r})'
        ).format(proper_repr(self._exponent), self._global_shift)

    def on(self, *args: raw_types.Qid,
           **kwargs: raw_types.Qid) -> raw_types.Operation:
        if not kwargs:
            return super().on(*args)
        if not args and set(kwargs.keys()) == {'control', 'target'}:
            return super().on(kwargs['control'], kwargs['target'])
        raise ValueError(
            "Expected two positional argument or else 'target' AND 'control' "
            "keyword arguments. But got args={!r}, kwargs={!r}.".format(
                args, kwargs))


def Rx(rads: value.TParamVal) -> XPowGate:
    """Returns a gate with the matrix e^{-i X rads / 2}."""
    pi = sympy.pi if protocols.is_parameterized(rads) else np.pi
    return XPowGate(exponent=rads / pi, global_shift=-0.5)


def Ry(rads: value.TParamVal) -> YPowGate:
    """Returns a gate with the matrix e^{-i Y rads / 2}."""
    pi = sympy.pi if protocols.is_parameterized(rads) else np.pi
    return YPowGate(exponent=rads / pi, global_shift=-0.5)


def Rz(rads: value.TParamVal) -> ZPowGate:
    """Returns a gate with the matrix e^{-i Z rads / 2}."""
    pi = sympy.pi if protocols.is_parameterized(rads) else np.pi
    return ZPowGate(exponent=rads / pi, global_shift=-0.5)


# The one qubit identity gate.
#
# Matrix:
#
#     [[1, 0],
#      [0, 1]]
I = IdentityGate(num_qubits=1)


# The Hadamard gate.
#
# Matrix:
#
#     [[s, s],
#      [s, -s]]
#     where s = sqrt(0.5).
H = HPowGate()

# The Clifford S gate.
#
# Matrix:
#
#     [[1, 0],
#      [0, i]]
S = ZPowGate(exponent=0.5)


# The non-Clifford T gate.
#
# Matrix:
#
#     [[1, 0]
#      [0, exp(i pi / 4)]]
T = ZPowGate(exponent=0.25)


# The controlled Z gate.
#
# Matrix:
#
#     [[1, 0, 0, 0],
#      [0, 1, 0, 0],
#      [0, 0, 1, 0],
#      [0, 0, 0, -1]]
CZ = CZPowGate()


# The controlled NOT gate.
#
# Matrix:
#
#     [[1, 0, 0, 0],
#      [0, 1, 0, 0],
#      [0, 0, 0, 1],
#      [0, 0, 1, 0]]
CNOT = CNotPowGate()
CX = CNOT
