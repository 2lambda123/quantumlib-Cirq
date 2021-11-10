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
import pytest
import sympy

import cirq
from cirq.ops.conditional_operation import ConditionalOperation

ALL_SIMULATORS = (
    cirq.Simulator(),
    cirq.DensityMatrixSimulator(),
    cirq.CliffordSimulator(),
)


def test_diagram():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.measure(q0, key='a'), cirq.X(q1).with_conditions('a'))

    cirq.testing.assert_has_diagram(
        circuit,
        """
0: ───M───────
      ║
1: ───╫───X───
      ║   ║
a: ═══@═══^═══
""",
        use_unicode_characters=True,
    )


def test_diagram_pauli():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.measure_single_paulistring(cirq.X(q0), key='a'),
        cirq.X(q1).with_conditions('a'),
    )

    cirq.testing.assert_has_diagram(
        circuit,
        """
0: ───M(X)───────
      ║
1: ───╫──────X───
      ║      ║
a: ═══@══════^═══
""",
        use_unicode_characters=True,
    )


def test_diagram_extra_measurements():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.measure(q0, key='a'),
        cirq.measure(q0, key='b'),
        cirq.X(q1).with_conditions('a'),
    )

    cirq.testing.assert_has_diagram(
        circuit,
        """
0: ───M───M('b')───
      ║
1: ───╫───X────────
      ║   ║
a: ═══@═══^════════
""",
        use_unicode_characters=True,
    )


def test_diagram_extra_controlled_bits():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.measure(q0, key='a'),
        cirq.CX(q0, q1).with_conditions('a'),
    )

    cirq.testing.assert_has_diagram(
        circuit,
        """
0: ───M───@───
      ║   ║
1: ───╫───X───
      ║   ║
a: ═══@═══^═══
""",
        use_unicode_characters=True,
    )


def test_diagram_extra_control_bits():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.measure(q0, key='a'),
        cirq.measure(q0, key='b'),
        cirq.X(q1).with_conditions(['a', 'b']),
    )

    cirq.testing.assert_has_diagram(
        circuit,
        """
0: ───M───M───────
      ║   ║
1: ───╫───╫───X───
      ║   ║   ║
a: ═══@═══╬═══^═══
          ║   ║
b: ═══════@═══^═══
""",
        use_unicode_characters=True,
    )


def test_diagram_multiple_ops_single_moment():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.measure(q0, key='a'),
        cirq.measure(q1, key='b'),
        cirq.X(q0).with_conditions('a'),
        cirq.X(q1).with_conditions('b'),
    )

    cirq.testing.assert_has_diagram(
        circuit,
        """
      ┌──┐   ┌──┐
0: ────M──────X─────
       ║      ║
1: ────╫M─────╫X────
       ║║     ║║
a: ════@╬═════^╬════
        ║      ║
b: ═════@══════^════
      └──┘   └──┘
""",
        use_unicode_characters=True,
    )


def test_diagram_subcircuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.CircuitOperation(
            cirq.FrozenCircuit(
                cirq.measure(q0, key='a'),
                cirq.X(q1).with_conditions('a'),
            )
        )
    )

    cirq.testing.assert_has_diagram(
        circuit,
        """
      Circuit_0x0000000000000000:
      [ 0: ───M───────          ]
0: ───[       ║                 ]───
      [ 1: ───╫───X───          ]
      [       ║   ║             ]
      [ a: ═══@═══^═══          ]
      │
1: ───#2────────────────────────────
""",
        use_unicode_characters=True,
    )


def test_diagram_subcircuit_layered():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.measure(q0, key='a'),
        cirq.CircuitOperation(
            cirq.FrozenCircuit(
                cirq.measure(q0, key='a'),
                cirq.X(q1).with_conditions('a'),
            ),
        ),
        ConditionalOperation(cirq.X(q1), ['a']),
    )

    cirq.testing.assert_has_diagram(
        circuit,
        """
          Circuit_0x0000000000000000:
          [ 0: ───M───────          ]
0: ───M───[       ║                 ]───────
      ║   [ 1: ───╫───X───          ]
      ║   [       ║   ║             ]
      ║   [ a: ═══@═══^═══          ]
      ║   ║
1: ───╫───#2────────────────────────────X───
      ║   ║                             ║
a: ═══@═══╩═════════════════════════════^═══
""",
        use_unicode_characters=True,
    )


def test_qasm():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.measure(q0, key='a'), cirq.X(q1).with_conditions('a'))
    qasm = cirq.qasm(circuit)
    assert (
        qasm
        == """// Generated from Cirq v0.14.0.dev

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [0, 1]
qreg q[2];
creg m_a[1];


measure q[0] -> m_a[0];
if (m_a!=0) x q[1];
"""
    )


@pytest.mark.parametrize('sim', ALL_SIMULATORS)
def test_key_unset(sim):
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.measure(q0, key='a'),
        cirq.X(q1).with_conditions('a'),
        cirq.measure(q1, key='b'),
    )
    result = sim.run(circuit)
    assert result.measurements['a'] == 0
    assert result.measurements['b'] == 0


@pytest.mark.parametrize('sim', ALL_SIMULATORS)
def test_key_set(sim):
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.X(q0),
        cirq.measure(q0, key='a'),
        cirq.X(q1).with_conditions('a'),
        cirq.measure(q1, key='b'),
    )
    result = sim.run(circuit)
    assert result.measurements['a'] == 1
    assert result.measurements['b'] == 1


@pytest.mark.parametrize('sim', ALL_SIMULATORS)
def test_subcircuit_key_unset(sim):
    q0, q1 = cirq.LineQubit.range(2)
    inner = cirq.Circuit(
        cirq.measure(q0, key='c'),
        cirq.X(q1).with_conditions('c'),
        cirq.measure(q1, key='b'),
    )
    circuit = cirq.Circuit(
        cirq.CircuitOperation(inner.freeze(), repetitions=2, measurement_key_map={'c': 'a'})
    )
    result = sim.run(circuit)
    assert result.measurements['0:a'] == 0
    assert result.measurements['0:b'] == 0
    assert result.measurements['1:a'] == 0
    assert result.measurements['1:b'] == 0


@pytest.mark.parametrize('sim', ALL_SIMULATORS)
def test_subcircuit_key_set(sim):
    q0, q1 = cirq.LineQubit.range(2)
    inner = cirq.Circuit(
        cirq.X(q0),
        cirq.measure(q0, key='c'),
        cirq.X(q1).with_conditions('c'),
        cirq.measure(q1, key='b'),
    )
    circuit = cirq.Circuit(
        cirq.CircuitOperation(inner.freeze(), repetitions=4, measurement_key_map={'c': 'a'})
    )
    result = sim.run(circuit)
    assert result.measurements['0:a'] == 1
    assert result.measurements['0:b'] == 1
    assert result.measurements['1:a'] == 0
    assert result.measurements['1:b'] == 1
    assert result.measurements['2:a'] == 1
    assert result.measurements['2:b'] == 0
    assert result.measurements['3:a'] == 0
    assert result.measurements['3:b'] == 0


def test_key_stacking():
    q0 = cirq.LineQubit(0)
    op = cirq.X(q0).with_conditions('a').with_tags('t').with_conditions('b')
    assert set(map(str, op.conditions)) == {'a', 'b'}
    assert not op.tags


def test_key_removal():
    q0 = cirq.LineQubit(0)
    op = cirq.X(q0).with_conditions('a').with_tags('t').with_conditions('b')
    op = op.unconditionally()
    assert not op.conditions
    assert set(map(str, op.tags)) == {'t'}


def test_qubit_mapping():
    q0, q1 = cirq.LineQubit.range(2)
    op = cirq.X(q0).with_conditions('a')
    assert op.with_qubits(q1).qubits == (q1,)


def test_parameterizable():
    s = sympy.Symbol('s')
    q0 = cirq.LineQubit(0)
    op = cirq.X(q0).with_conditions('a')
    opa = ConditionalOperation(cirq.XPowGate(exponent=s).on(q0), ['a'])
    assert cirq.is_parameterized(opa)
    assert not cirq.is_parameterized(op)
    assert cirq.resolve_parameters(opa, cirq.ParamResolver({'s': 1})) == op


def test_decompose():
    q0 = cirq.LineQubit(0)
    op = cirq.H(q0).with_conditions('a')
    assert cirq.decompose(op) == [
        (cirq.Y(q0) ** 0.5).with_conditions('a'),
        cirq.XPowGate(exponent=1.0, global_shift=-0.25).on(q0).with_conditions('a'),
    ]


def test_str():
    q0 = cirq.LineQubit(0)
    op = cirq.X(q0).with_conditions('a')
    assert (
        str(op)
        == "ConditionalOperation(cirq.X(cirq.LineQubit(0)), [cirq.MeasurementKey(name='a')])"
    )
