# Copyright 2022 The Cirq Developers
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
import abc
from typing import Collection, Tuple, TYPE_CHECKING, Any, Dict, Iterator, Optional, Sequence, Union
import itertools

from cirq import protocols, value

if TYPE_CHECKING:
    import cirq


@value.value_equality
class AbstractControlValues(abc.ABC):
    """Abstract base class defining the API for control values.

    `AbstractControlValues` is an abstract class that defines the API for control values
    and implements functions common to all implementations (e.g.  comparison).

    `cirq.ControlledGate` and `cirq.ControlledOperation` are useful to augment
    existing gates and operations to have one or more control qubits. For every
    control qubit, the set of integer values for which the control should be enabled
    is represented by one of the implementations of `cirq.AbstractControlValues`.

    Implementations of `cirq.AbstractControlValues` can use different internal
    representations to store control values, but they must satisfy the public API
    defined here and be immutable.
    """

    @abc.abstractmethod
    def validate(self, qid_shapes: Sequence[int]) -> None:
        """Validates that all control values for ith qubit are in range [0, qid_shaped[i])"""

    @abc.abstractmethod
    def expand(self) -> 'SumOfProducts':
        """Returns an expanded `cirq.SumOfProduct` representation of this control values."""

    @property
    @abc.abstractmethod
    def is_trivial(self) -> bool:
        """Returns True iff each controlled variable is activated only for value 1.

        This configuration is equivalent to `cirq.SumOfProducts(((1,) * num_controls))`
        and `cirq.ProductOfSums(((1,),) * num_controls)`

        """

    @abc.abstractmethod
    def _num_qubits_(self) -> int:
        """Returns the number of qubits for which control values are stored by this object."""

    @abc.abstractmethod
    def _json_dict_(self) -> Dict[str, Any]:
        """Returns a dictionary used for serializing this object."""

    @abc.abstractmethod
    def _circuit_diagram_info_(
        self, args: 'cirq.CircuitDiagramInfoArgs'
    ) -> 'cirq.CircuitDiagramInfo':
        """Returns information used to draw this object in circuit diagrams."""

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Tuple[int, ...]]:
        """Iterator on internal representation of control values used by the derived classes.

        Note: Be careful that the terms iterated upon by this iterator will have different
        meaning based on the implementation. For example:
        >>> print(*cirq.ProductOfSums([(0, 1), (0,)]))
        (0, 1) (0,)
        >>> print(*cirq.SumOfProducts([(0, 0), (1, 0)]))
        (0, 0) (1, 0)
        """

    def _value_equality_values_(self) -> Any:
        return tuple(v for v in self.expand())

    def __and__(self, other: 'AbstractControlValues') -> 'AbstractControlValues':
        """Sets self to be the cartesian product of all combinations in self x other.

        Args:
          other: An object that implements AbstractControlValues.

        Returns:
          An object that represents the cartesian product of the two inputs.
        """
        return SumOfProducts(
            tuple(x + y for (x, y) in itertools.product(self.expand(), other.expand()))
        )


class ProductOfSums(AbstractControlValues):
    """ProductOfSums represents control values in a form of a cartesian product of tuples."""

    def __init__(self, data: Sequence[Union[int, Collection[int]]]):
        self._internal_representation = tuple(
            (cv,) if isinstance(cv, int) else tuple(sorted(frozenset(cv))) for cv in data
        )
        self._is_trivial = self._internal_representation == ((1,),) * len(
            self._internal_representation
        )

    @property
    def is_trivial(self) -> bool:
        return self._is_trivial

    def __iter__(self) -> Iterator[Tuple[int, ...]]:
        return iter(self._internal_representation)

    def expand(self) -> 'SumOfProducts':
        return SumOfProducts(tuple(itertools.product(*self._internal_representation)))

    def __repr__(self) -> str:
        return f'cirq.ProductOfSums({str(self._internal_representation)})'

    def _num_qubits_(self) -> int:
        return len(self._internal_representation)

    def __getitem__(self, key: Union[int, slice]) -> Union['ProductOfSums', Tuple[int, ...]]:
        if isinstance(key, slice):
            return ProductOfSums(self._internal_representation[key])
        return self._internal_representation[key]

    def validate(self, qid_shapes: Sequence[int]) -> None:
        for i, (vals, shape) in enumerate(zip(self._internal_representation, qid_shapes)):
            if not all(0 <= v < shape for v in vals):
                message = (
                    f'Control values <{vals!r}> outside of range for control qubit '
                    f'number <{i}>.'
                )
                raise ValueError(message)

    def _circuit_diagram_info_(
        self, args: 'cirq.CircuitDiagramInfoArgs'
    ) -> 'cirq.CircuitDiagramInfo':
        """Returns a string representation to be used in circuit diagrams."""

        def get_symbol(vals):
            return '@' if tuple(vals) == (1,) else f"({','.join(map(str, vals))})"

        return protocols.CircuitDiagramInfo(
            wire_symbols=[get_symbol(t) for t in self._internal_representation]
        )

    def __str__(self) -> str:
        if self.is_trivial:
            return 'C' * self._num_qubits_()

        def get_prefix(control_vals):
            control_vals_str = ''.join(map(str, sorted(control_vals)))
            return f'C{control_vals_str}'

        return ''.join(get_prefix(t) for t in self._internal_representation)

    def _json_dict_(self) -> Dict[str, Any]:
        return {"data": self._internal_representation}

    def __and__(self, other: AbstractControlValues) -> AbstractControlValues:
        if isinstance(other, ProductOfSums):
            return ProductOfSums(self._internal_representation + other._internal_representation)
        return super().__and__(other)


class SumOfProducts(AbstractControlValues):
    """Represents control values as a union of n-bit tuples.

    `SumOfProducts` representation describes the control values as a union
    of n-bit tuples, where each n-bit tuple represents an allowed assignment
    of bits for which the control should be activated. This expanded
    representation allows us to create control values combinations which
    cannot be factored as a `ProductOfSums` representation.

    For example:

    1) `(|00><00| + |11><11|) X + (|01><01| + |10><10|) I` represents an
        operator which flips the third qubit if the first two qubits
        are `00` or `11`, and does nothing otherwise.
        This can be constructed as
        >>> xor_control_values = cirq.SumOfProducts(((0, 0), (1, 1)))
        >>> q0, q1, q2 = cirq.LineQubit.range(3)
        >>> xor_cop = cirq.X(q2).controlled_by(q0, q1, control_values=xor_control_values)

    2) `(|00><00| + |01><01| + |10><10|) X + (|11><11|) I` represents an
        operators which flips the third qubit if the `nand` of first two
        qubits is `1` (i.e. first two qubits are either `00`, `01` or `10`),
        and does nothing otherwise. This can be constructed as:

        >>> nand_control_values = cirq.SumOfProducts(((0, 0), (0, 1), (1, 0)))
        >>> q0, q1, q2 = cirq.LineQubit.range(3)
        >>> nand_cop = cirq.X(q2).controlled_by(q0, q1, control_values=nand_control_values)
    """

    def __init__(self, data: Sequence[Union[int, Collection[int]]], *, name: Optional[str] = None):
        self._internal_representation = tuple(
            sorted(frozenset((cv,) if isinstance(cv, int) else tuple(cv) for cv in data))
        )
        self._name = name
        if not len(self._internal_representation):
            raise ValueError("SumOfProducts can't be empty.")
        num_qubits = len(self._internal_representation[0])
        if not all(len(p) == num_qubits for p in self._internal_representation):
            raise ValueError(
                f'Each term of {self._internal_representation} should be of length {num_qubits}.'
            )
        self._is_trivial = self._internal_representation == (
            (1,) * len(self._internal_representation[0]),
        )

    @property
    def is_trivial(self) -> bool:
        return self._is_trivial

    def expand(self) -> 'SumOfProducts':
        return self

    def __iter__(self) -> Iterator[Tuple[int, ...]]:
        """Returns the combinations tracked by the object."""
        return iter(self._internal_representation)

    def _circuit_diagram_info_(
        self, args: 'cirq.CircuitDiagramInfoArgs'
    ) -> 'cirq.CircuitDiagramInfo':
        """Returns a string representation to be used in circuit diagrams."""
        if self._name is not None:
            wire_symbols = ['@'] * self._num_qubits_()
            wire_symbols[-1] = f'@({self._name})'
            return protocols.CircuitDiagramInfo(wire_symbols=wire_symbols)

        wire_symbols = [''] * self._num_qubits_()
        for term in self._internal_representation:
            for q_i, q_val in enumerate(term):
                wire_symbols[q_i] = wire_symbols[q_i] + str(q_val)
        wire_symbols = [f'@({s})' for s in wire_symbols]
        return protocols.CircuitDiagramInfo(wire_symbols=wire_symbols)

    def __repr__(self) -> str:
        name = '' if self._name is None else f', name="{self._name}"'
        return f'cirq.SumOfProducts({self._internal_representation!s} {name})'

    def __str__(self) -> str:
        suffix = (
            self._name
            if self._name is not None
            else '_'.join(''.join(str(v) for v in t) for t in self._internal_representation)
        )
        return f'C_{suffix}'

    def _num_qubits_(self) -> int:
        return len(self._internal_representation[0])

    def validate(self, qid_shapes: Sequence[int]) -> None:
        if len(qid_shapes) != self._num_qubits_():
            raise ValueError(
                f'Length of qid_shapes: {qid_shapes} should be equal to self._num_qubits_():'
                f' {self._num_qubits_()}'
            )

        for product in self._internal_representation:
            for q_i, q_val in enumerate(product):
                if not (0 <= q_val < qid_shapes[q_i]):
                    raise ValueError(
                        f'Control value <{q_val}> in combination {product} is outside'
                        f' of range [0, {qid_shapes[q_i]}) for control qubit number <{q_i}>.'
                    )

    def _json_dict_(self) -> Dict[str, Any]:
        return {'data': self._internal_representation, 'name': self._name}
