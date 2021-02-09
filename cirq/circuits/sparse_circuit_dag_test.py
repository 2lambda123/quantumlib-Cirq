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

import cirq
import pytest
from cirq.circuits import SparseCircuitDag


def test_from_ops_by_moment_index():
    circuit = cirq.Circuit()
    q0, q1, q2 = cirq.LineQubit.range(3)
    circuit.append([cirq.CZ(q0, q1), cirq.H(q2), cirq.H(q0), cirq.CZ(q1, q2)])
    circuit_ops_by_reverse_moment_index = (
            (3-index, op) for index, moment in enumerate(circuit.moments) for op in moment.operations
        )
    with pytest.raises(ValueError, match="Moment indices expected to increase."):
        _ = SparseCircuitDag.from_ops_by_moment_index(
            circuit_ops_by_reverse_moment_index, device=circuit.device
        )


def test_factorize_simple_circuit_one_factor():
    circuit = cirq.Circuit()
    q0, q1, q2 = cirq.LineQubit.range(3)
    circuit.append([cirq.CZ(q0, q1), cirq.H(q2), cirq.H(q0), cirq.CZ(q1, q2)])
    dag = cirq.SparseCircuitDag.from_circuit(circuit)
    factors = list(dag.factorize())
    assert len(factors) == 1
    desired = """
0: ───@───H───
      │
1: ───@───@───
          │
2: ───H───@───
"""
    cirq.testing.assert_has_diagram(factors[0].to_circuit(), desired)


def test_factorize_simple_circuit_two_factors():
    circuit = cirq.Circuit()
    q0, q1, q2 = cirq.LineQubit.range(3)
    circuit.append([cirq.H(q1), cirq.CZ(q0, q1), cirq.H(q2), cirq.H(q0), cirq.H(q0)])
    dag = cirq.SparseCircuitDag.from_circuit(circuit)
    factors = list(dag.factorize())
    assert len(factors) == 2
    desired = [
        """
0: ───────@───H───H───
          │
1: ───H───@───────────
""",
        """
2: ───H───
""",
    ]
    for f, d in zip(factors, desired):
        cirq.testing.assert_has_diagram(f.to_circuit(), d)


def test_large_circuit():
    circuit = cirq.Circuit()
    qubits = cirq.GridQubit.rect(3, 3)
    circuit.append(cirq.Moment(cirq.X(q) for q in qubits))
    pairset = [[(0, 2), (4, 6)], [(1, 2), (4, 8)]]
    for pairs in pairset:
        circuit.append(cirq.Moment(cirq.CZ(qubits[a], qubits[b]) for (a, b) in pairs))
    circuit.append(cirq.Moment(cirq.Y(q) for q in qubits))
    # expect 5 factors
    dag = cirq.SparseCircuitDag.from_circuit(circuit)
    factors = list(dag.factorize())
    desired = [
        """
(0, 0): ───X───@───────Y───
               │
(0, 1): ───X───┼───@───Y───
               │   │
(0, 2): ───X───@───@───Y───
""",
        """
(1, 0): ───X───Y───
""",
        """
(1, 1): ───X───@───@───Y───
               │   │
(2, 0): ───X───@───┼───Y───
                   │
(2, 2): ───X───────@───Y───
""",
        """
(1, 2): ───X───Y───
""",
        """
(2, 1): ───X───Y───
    """,
    ]
    assert len(factors) == 5
    for f, d in zip(factors, desired):
        cirq.testing.assert_has_diagram(f.to_circuit(), d)
