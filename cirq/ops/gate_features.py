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

"""Marker classes for indicating which additional features gates support.

For example: some gates are reversible, some have known matrices, etc.
"""

from typing import Any, Dict, Optional, Sequence, Tuple, Iterable

import abc
import string

from cirq.ops import op_tree, raw_types


class InterchangeableQubitsGate(metaclass=abc.ABCMeta):
    """Indicates operations should be equal under some qubit permutations."""

    def qubit_index_to_equivalence_group_key(self, index: int) -> int:
        """Returns a key that differs between non-interchangeable qubits."""
        return 0


class CompositeOperation(metaclass=abc.ABCMeta):
    """An operation with a known decomposition into simpler operations."""

    @abc.abstractmethod
    def default_decompose(self) -> op_tree.OP_TREE:
        """Yields simpler operations for performing the receiving operation."""


class CompositeGate(metaclass=abc.ABCMeta):
    """A gate with a known decomposition into simpler gates."""

    @abc.abstractmethod
    def default_decompose(
            self, qubits: Sequence[raw_types.QubitId]) -> op_tree.OP_TREE:
        """Yields operations for performing this gate on the given qubits.

        Args:
            qubits: The qubits the gate should be applied to.
        """


class TextDiagramInfoArgs:
    """
    Attributes:
        known_qubits: The qubits the gate is being applied to. None means this
            information is not known by the caller.
        known_qubit_count: The number of qubits the gate is being applied to
            None means this information is not known by the caller.
        use_unicode_characters: If true, the wire symbols are permitted to
            include unicode characters (as long as they work well in fixed
            width fonts). If false, use only ascii characters. ASCII is
            preferred in cases where UTF8 support is done poorly, or where
            the fixed-width font being used to show the diagrams does not
            properly handle unicode characters.
        precision: The number of digits after the decimal to show for numbers in
            the text diagram. None means use full precision.
        qubit_map: The map from qubits to diagram positions.
    """

    UNINFORMED_DEFAULT = None  # type: TextDiagramInfoArgs

    def __init__(self,
                 known_qubits: Optional[Tuple[raw_types.QubitId, ...]],
                 known_qubit_count: Optional[int],
                 use_unicode_characters: bool,
                 precision: Optional[int],
                 qubit_map: Optional[Dict[raw_types.QubitId, int]]) -> None:
        self.known_qubits = known_qubits
        self.known_qubit_count = known_qubit_count
        self.use_unicode_characters = use_unicode_characters
        self.precision = precision
        self.qubit_map = qubit_map


TextDiagramInfoArgs.UNINFORMED_DEFAULT = TextDiagramInfoArgs(
    known_qubits=None,
    known_qubit_count=None,
    use_unicode_characters=True,
    precision=3,
    qubit_map=None)


class TextDiagramInfo:
    def __init__(self,
                 wire_symbols: Tuple[str, ...],
                 exponent: Any = 1,
                 connected: bool = True) -> None:
        """
        Args:
            wire_symbols: The symbols that should be shown on the qubits
                affected by this operation. Must match the number of qubits that
                the operation is applied to.
            exponent: An optional convenience value that will be appended onto
                an operation's final gate symbol with a caret in front
                (unless it's equal to 1). For example, the square root of X gate
                has a text diagram exponent of 0.5 and symbol of 'X' so it is
                drawn as 'X^0.5'.
            connected: Whether or not to draw a line connecting the qubits.
        """
        self.wire_symbols = wire_symbols
        self.exponent = exponent
        self.connected = connected

    def _eq_tuple(self):
        return (TextDiagramInfo, self.wire_symbols,
                self.exponent, self.connected)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._eq_tuple() == other._eq_tuple()

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._eq_tuple())

    def __repr__(self):
        return ('cirq.TextDiagramInfo(' +
                'wire_symbols={!r}, '.format(self.wire_symbols) +
                'exponent={!r}, '.format(self.exponent) +
                'connected={!r})'.format(self.connected)
                )


class TextDiagrammable(metaclass=abc.ABCMeta):
    """A thing which can be printed in a text diagram."""

    @abc.abstractmethod
    def text_diagram_info(self, args: TextDiagramInfoArgs) -> TextDiagramInfo:
        """Describes how to draw something in a text diagram.

        Args:
            args: A TextDiagramInfoArgs instance encapsulating various pieces of
                information (e.g. how many qubits are we being applied to) as
                well as user options (e.g. whether to avoid unicode characters).

        Returns:
             A TextDiagramInfo instance describing what to print.
        """


class SingleQubitGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate that must be applied to exactly one qubit."""

    def validate_args(self, qubits):
        if len(qubits) != 1:
            raise ValueError(
                'Single-qubit gate applied to multiple qubits: {}({})'.
                format(self, qubits))

    def on_each(self, targets: Iterable[raw_types.QubitId]) -> op_tree.OP_TREE:
        """Returns a list of operations apply this gate to each of the targets.

        Args:
            targets: The qubits to apply this gate to.

        Returns:
            Operations applying this gate to the target qubits.
        """
        return [self.on(target) for target in targets]


class TwoQubitGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate that must be applied to exactly two qubits."""

    def validate_args(self, qubits):
        if len(qubits) != 2:
            raise ValueError(
                'Two-qubit gate not applied to two qubits: {}({})'.
                format(self, qubits))


class ThreeQubitGate(raw_types.Gate, metaclass=abc.ABCMeta):
    """A gate that must be applied to exactly three qubits."""

    def validate_args(self, qubits):
        if len(qubits) != 3:
            raise ValueError(
                'Three-qubit gate not applied to three qubits: {}({})'.
                format(self, qubits))



class QasmOutputArgs(string.Formatter):
    """
    Attributes:
        precision: The number of digits after the decimal to show for numbers in
            the text diagram.
        version: The QASM version to output.  QasmConvertibleGate/Operation may
            return different text depending on version.
        qubit_id_map: A dictionary mapping qubits to qreg QASM identifiers.
        meas_key_id_map: A dictionary mapping measurement keys to creg QASM
            identifiers.
    """
    def __init__(self,
                 precision: int = 10,
                 version: str = '2.0',
                 qubit_id_map: Dict[raw_types.QubitId, str] = None,
                 meas_key_id_map: Dict[str, str] = None,
                 ) -> None:
        self.precision = precision
        self.version = version
        self.qubit_id_map = {} if qubit_id_map is None else qubit_id_map
        self.meas_key_id_map = ({} if meas_key_id_map is None
                                   else meas_key_id_map)

    def format_field(self, value: Any, spec: str) -> str:
        """Method of string.Formatter that specifies the output of format()."""
        if isinstance(value, float):
            value = round(value, self.precision)
            if spec == 'half_turns':
                value = 'pi*{}'.format(value) if value != 0 else '0'
                spec = ''
        elif isinstance(value, raw_types.QubitId):
            value = self.qubit_id_map[value]
        elif isinstance(value, str) and spec == 'meas':
            value = self.meas_key_id_map[value]
            spec = ''
        return super().format_field(value, spec)

    def validate_version(self, *supported_versions: str) -> None:
        if self.version not in supported_versions:
            raise ValueError('QASM version {} output is not supported.'.format(
                                self.version))


class QasmConvertibleGate(metaclass=abc.ABCMeta):
    """A gate that knows its representation in QASM."""
    @abc.abstractmethod
    def known_qasm_output(self,
                          qubits: Tuple[raw_types.QubitId, ...],
                          args: QasmOutputArgs) -> Optional[str]:
        """Returns lines of QASM output representing the gate on the given
        qubits or None if a simple conversion is not possible.
        """


class QasmConvertibleOperation(metaclass=abc.ABCMeta):
    """An operation that knows its representation in QASM."""
    @abc.abstractmethod
    def known_qasm_output(self, args: QasmOutputArgs) -> Optional[str]:
        """Returns lines of QASM output representing the operation or None if a
        simple conversion is not possible."""
