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

from typing import List
from cirq import abc
from cirq.google import XmonDevice
from cirq.line import LineQubit
from cirq.line.placement.sequence import LinePlacement


class LinePlacementMethod(metaclass=abc.ABCMeta):
    """Choice and options for the line placement calculation method.

    Currently two methods are available: cirq.line.GreedySequenceSearchMethod
    and cirq.line.AnnealSequenceSearchMethod.
    """

    @abc.abstractmethod
    def place_line(self,
                   device: XmonDevice,
                   qubits: List[LineQubit]) -> LinePlacement:
        """Runs line sequence search.

        Args:
            device: Chip description.
            qubits: List of qubits to find the placement for.

        Returns:
            Linear sequences found on the chip.
        """
        pass
