# Copyright 2021 The Cirq Developers
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

# This is more of a placeholder for now, we can add
# official color schemes in follow-ups.
import abc
import dataclasses
from typing import List, Optional
import cirq


@dataclasses.dataclass
class SymbolInfo:
    """Organizes information about a symbol."""

    labels: List[str]
    colors: List[str]

    @staticmethod
    def unknown_operation(num_qubits: int) -> 'SymbolInfo':
        symbol_info = SymbolInfo([], [])
        for _ in range(num_qubits):
            symbol_info.colors.append('gray')
            symbol_info.labels.append('?')
        return symbol_info


class SymbolResolver(metaclass=abc.ABCMeta):
    """Abstract class providing the interface for users to specify information
    about how a particular symbol should be displayed in the 3D circuit
    """

    def __call__(self, operation: cirq.Operation) -> Optional[SymbolInfo]:
        return self.resolve(operation)

    @abc.abstractmethod
    def resolve(self, operation: cirq.Operation) -> Optional[SymbolInfo]:
        pass


class DefaultResolver(SymbolResolver):
    """Default symbol resolver implementation. Takes information
    from circuit_diagram_info, if unavailable, returns information representing
    an unknown symbol.
    """

    _SYMBOL_COLORS = {
        '@': 'black',
        'H': 'yellow',
        'I': 'orange',
        'X': 'black',
        'Y': 'pink',
        'Z': 'cyan',
        'S': '#90EE90',
        'T': '#CBC3E3',
    }

    def resolve(self, operation: cirq.Operation) -> Optional[SymbolInfo]:
        try:
            wire_symbols = cirq.circuit_diagram_info(operation).wire_symbols
            if wire_symbols is NotImplemented:
                return SymbolInfo.unknown_operation(cirq.num_qubits(operation))
        except TypeError:
            return SymbolInfo.unknown_operation(cirq.num_qubits(operation))

        symbol_info = SymbolInfo(list(wire_symbols), [])
        for symbol in wire_symbols:
            symbol_info.colors.append(DefaultResolver._SYMBOL_COLORS.get(symbol, 'gray'))

        return symbol_info


DEFAULT_SYMBOL_RESOLVERS: List[SymbolResolver] = [DefaultResolver()]


def resolve_operation(
    operation: cirq.Operation, resolvers: List[SymbolResolver]
) -> Optional[SymbolInfo]:
    symbol_info = None
    for resolver in resolvers:
        info = resolver(operation)
        if info is not None:
            symbol_info = info
    return symbol_info


## 3D symbol resolver
## takes an operation, if it matches the operation, returns back how to build it
# I, xpow, ypow, zpow
# lambda expresssion
class Operation3DSymbol:
    def __init__(self, wire_symbols, location_info, color_info, moment):
        """Gathers symbol information from an operation and builds an
        object to represent it in 3D.

        Args:
            wire_symbols: a list of symbols taken from circuit_diagram_info()
            that will be used to represent the operation in the 3D circuit.

            location_info: A list of coordinates for each wire_symbol. The
            index of the coordinate tuple in the location_info list must
            correspond with the index of the symbol in the wire_symbols list.

            color_info: a list representing the desired color of the symbol(s).
            These will also correspond to index of the symbol in the
            wire_symbols list.

            moment: the moment where the symbol should be.
        """
        self.wire_symbols = wire_symbols
        self.location_info = location_info
        self.color_info = color_info
        self.moment = moment

    def to_typescript(self):
        return {
            'wire_symbols': list(self.wire_symbols),
            'location_info': self.location_info,
            'color_info': self.color_info,
            'moment': self.moment,
        }
