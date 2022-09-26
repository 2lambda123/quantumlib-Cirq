# Copyright 2019 The Cirq Developers
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
"""Tests for IonQ native gates"""

import math
import cirq
import numpy
import pytest

import cirq_ionq as ionq


@pytest.mark.parametrize(
    "gate,nqubits,diagram",
    [
        (ionq.GPIGate(phi=0.1), 1, "0: ───GPI(0.1)───"),
        (ionq.GPI2Gate(phi=0.2), 1, "0: ───GPI2(0.2)───"),
        (ionq.MSGate(phi0=0.1, phi1=0.2), 2, "0: ───MS(0.1)───\n      │\n1: ───MS(0.2)───"),
    ],
)
def test_gate_methods(gate, nqubits, diagram):
    assert str(gate) != ""
    assert repr(gate) != ""
    assert gate.num_qubits() == nqubits
    assert cirq.protocols.circuit_diagram_info(gate) is not None
    c = cirq.Circuit()
    c.append([gate.on(*cirq.LineQubit.range(nqubits))])
    assert c.to_text_diagram() == diagram


@pytest.mark.parametrize(
    "gate", [ionq.GPIGate(phi=0.1), ionq.GPI2Gate(phi=0.2), ionq.MSGate(phi0=0.1, phi1=0.2)]
)
def test_gate_json(gate):
    g_json = cirq.to_json(gate)
    assert cirq.read_json(json_text=g_json) == gate


@pytest.mark.parametrize("phase", [0, 0.1, 0.4, math.pi / 2, math.pi, 2 * math.pi])
def test_gpi_unitary(phase):
    """Tests that the GPI gate is unitary."""
    gate = ionq.GPIGate(phi=phase)

    mat = cirq.protocols.unitary(gate)
    numpy.testing.assert_array_almost_equal(mat.dot(mat.conj().T), numpy.identity(2))


@pytest.mark.parametrize("phase", [0, 0.1, 0.4, math.pi / 2, math.pi, 2 * math.pi])
def test_gpi2_unitary(phase):
    """Tests that the GPI2 gate is unitary."""
    gate = ionq.GPI2Gate(phi=phase)

    mat = cirq.protocols.unitary(gate)
    numpy.testing.assert_array_almost_equal(mat.dot(mat.conj().T), numpy.identity(2))


@pytest.mark.parametrize(
    "phases", [(0, 1), (0.1, 1), (0.4, 1), (math.pi / 2, 0), (0, math.pi), (0.1, 2 * math.pi)]
)
def test_ms_unitary(phases):
    """Tests that the MS gate is unitary."""
    gate = ionq.MSGate(phi0=phases[0], phi1=phases[1])

    mat = cirq.protocols.unitary(gate)
    numpy.testing.assert_array_almost_equal(mat.dot(mat.conj().T), numpy.identity(4))


@pytest.mark.parametrize(
    "gate,target,phases",
    [
        (ionq.GPIGate, numpy.identity(2), {"phi": p})
        for p in [0, 0.1, 0.4, math.pi / 2, math.pi, 2 * math.pi]
    ]
    + [
        (ionq.GPI2Gate, numpy.identity(2), {"phi": p})
        for p in [0, 0.1, 0.4, math.pi / 2, math.pi, 2 * math.pi]
    ]
    + [
        (ionq.MSGate, numpy.identity(4), {"phi0": p0, "phi1": p1})
        for p0, p1 in [
            (0, 1),
            (0.1, 1),
            (0.4, 1),
            (math.pi / 2, 0),
            (0, math.pi),
            (0.1, 2 * math.pi),
        ]
    ],
)
def test_gate_inverse(gate, target, phases):
    """Tests that the inverse of natives gate are correct."""
    gate_bound = gate(**phases)
    mat = cirq.protocols.unitary(gate_bound)
    mat_inverse = cirq.protocols.unitary(gate_bound**-1)

    numpy.testing.assert_array_almost_equal(mat.dot(mat_inverse), target)


@pytest.mark.parametrize(
    "gate,phases",
    [(ionq.GPIGate, {"phi": p}) for p in [0, 0.1, 0.4, math.pi / 2, math.pi, 2 * math.pi]]
    + [(ionq.GPI2Gate, {"phi": p}) for p in [0, 0.1, 0.4, math.pi / 2, math.pi, 2 * math.pi]]
    + [
        (ionq.MSGate, {"phi0": p0, "phi1": p1})
        for p0, p1 in [
            (0, 1),
            (0.1, 1),
            (0.4, 1),
            (math.pi / 2, 0),
            (0, math.pi),
            (0.1, 2 * math.pi),
        ]
    ],
)
def test_gate_power1(gate, phases):
    """Tests that power=1 for native gates are correct."""
    gate_bound = gate(**phases)
    mat = cirq.protocols.unitary(gate_bound)
    mat_power1 = cirq.protocols.unitary(gate_bound**1)

    numpy.testing.assert_array_almost_equal(mat, mat_power1)


@pytest.mark.parametrize(
    "gate,power",
    [(ionq.GPIGate(phi=0.1), power) for power in [-2, -0.5, 0, 0.5, 2]]
    + [(ionq.GPI2Gate(phi=0.1), power) for power in [-2, -0.5, 0, 0.5, 2]]
    + [(ionq.MSGate(phi0=0.1, phi1=0.2), power) for power in [-2, -0.5, 0, 0.5, 2]],
)
def test_gate_power_not_implemented(gate, power):
    """Tests that any power other than 1 and -1 is not implemented."""
    with pytest.raises(TypeError):
        gate**power
