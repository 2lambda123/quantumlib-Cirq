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
import functools
import itertools
import math
import random

import numpy as np
import pytest
import sympy.parsing.sympy_parser as sympy_parser

import cirq
import cirq.ops.boolean_hamiltonian as bh


@pytest.mark.parametrize(
    'boolean_str',
    [
        'x0',
        '~x0',
        'x0 ^ x1',
        'x0 & x1',
        'x0 | x1',
        'x0 & x1 & x2',
        'x0 & x1 & ~x2',
        'x0 & ~x1 & x2',
        'x0 & ~x1 & ~x2',
        '~x0 & x1 & x2',
        '~x0 & x1 & ~x2',
        '~x0 & ~x1 & x2',
        '~x0 & ~x1 & ~x2',
        'x0 ^ x1 ^ x2',
        'x0 | (x1 & x2)',
        'x0 & (x1 | x2)',
        '(x0 ^ x1 ^ x2) | (x2 ^ x3 ^ x4)',
        '(x0 ^ x2 ^ x4) | (x1 ^ x2 ^ x3)',
        'x0 & x1 & (x2 | x3)',
        'x0 & ~x2',
        '~x0 & x2',
        'x2 & ~x0',
        '~x2 & x0',
        '(x2 | x1) ^ x0',
    ],
)
def test_circuit(boolean_str):
    boolean_expr = sympy_parser.parse_expr(boolean_str)
    var_names = cirq.parameter_names(boolean_expr)
    qubits = [cirq.NamedQubit(name) for name in var_names]

    # We use Sympy to evaluate the expression:
    n = len(var_names)

    expected = []
    for binary_inputs in itertools.product([0, 1], repeat=n):
        subed_expr = boolean_expr
        for var_name, binary_input in zip(var_names, binary_inputs):
            subed_expr = subed_expr.subs(var_name, binary_input)
        expected.append(bool(subed_expr))

    # We build a circuit and look at its output state vector:
    circuit = cirq.Circuit()
    circuit.append(cirq.H.on_each(*qubits))

    hamiltonian_gate = cirq.BooleanHamiltonian(
        {q.name: q for q in qubits}, [boolean_str], 0.1 * math.pi
    )
    assert hamiltonian_gate.with_qubits(*qubits) == hamiltonian_gate

    assert hamiltonian_gate.num_qubits() == n

    circuit.append(hamiltonian_gate)

    phi = cirq.Simulator().simulate(circuit, qubit_order=qubits, initial_state=0).state_vector()
    actual = np.arctan2(phi.real, phi.imag) - math.pi / 2.0 > 0.0

    # Compare the two:
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize(
    'n_bits,expected_hs',
    [
        (1, [(), (0,)]),
        (2, [(), (0,), (0, 1), (1,)]),
        (3, [(), (0,), (0, 1), (1,), (1, 2), (0, 1, 2), (0, 2), (2,)]),
    ],
)
def test_gray_code_sorting(n_bits, expected_hs):
    hs = []
    for x in range(2 ** n_bits):
        h = []
        for i in range(n_bits):
            if x % 2 == 1:
                h.append(i)
                x -= 1
            x //= 2
        hs.append(tuple(sorted(h)))
    random.shuffle(hs)

    sorted_hs = sorted(list(hs), key=functools.cmp_to_key(bh._gray_code_comparator))

    np.testing.assert_array_equal(sorted_hs, expected_hs)


@pytest.mark.parametrize(
    'seq_a,seq_b,expected',
    [
        ((), (), 0),
        ((), (0,), -1),
        ((0,), (), 1),
        ((0,), (0,), 0),
    ],
)
def test_gray_code_comparison(seq_a, seq_b, expected):
    assert bh._gray_code_comparator(seq_a, seq_b) == expected


@pytest.mark.parametrize(
    'input_cnots,input_flip_control_and_target,expected_simplified,expected_output_cnots',
    [
        # Empty inputs don't get simplified.
        ([], False, False, []),
        ([], True, False, []),
        # Single CNOTs don't get simplified.
        ([(0, 1)], False, False, [(0, 1)]),
        ([(0, 1)], True, False, [(0, 1)]),
        # Simplify away two CNOTs that are identical:
        ([(0, 1), (0, 1)], False, True, []),
        ([(0, 1), (0, 1)], True, True, []),
        # Also simplify away if there's another CNOT in between.
        ([(0, 1), (2, 1), (0, 1)], False, True, [(2, 1)]),
        ([(0, 1), (0, 2), (0, 1)], True, True, [(0, 2)]),
        # However, the in-between has to share the same target/control.
        ([(0, 1), (0, 2), (0, 1)], False, False, [(0, 1), (0, 2), (0, 1)]),
        ([(0, 1), (2, 1), (0, 1)], True, False, [(0, 1), (2, 1), (0, 1)]),
    ],
)
def test_simplify_commuting_cnots(
    input_cnots, input_flip_control_and_target, expected_simplified, expected_output_cnots
):
    actual_simplified, actual_output_cnots = bh._simplify_commuting_cnots(
        input_cnots, input_flip_control_and_target
    )
    assert actual_simplified == expected_simplified
    assert actual_output_cnots == expected_output_cnots


@pytest.mark.parametrize(
    'input_cnots,input_flip_control_and_target,expected_simplified,expected_output_cnots',
    [
        # Empty inputs don't get simplified.
        ([], False, False, []),
        ([], True, False, []),
        # Single CNOTs don't get simplified.
        ([(0, 1)], False, False, [(0, 1)]),
        ([(0, 1)], True, False, [(0, 1)]),
        # Simplify according to equation 11 of [4].
        ([(2, 1), (2, 0), (1, 0)], False, True, [(1, 0), (2, 1)]),
        ([(1, 2), (0, 2), (0, 1)], True, True, [(0, 1), (1, 2)]),
    ],
)
def test_simplify_cnots_triplets(
    input_cnots, input_flip_control_and_target, expected_simplified, expected_output_cnots
):
    actual_simplified, actual_output_cnots = bh._simplify_cnots_triplets(
        input_cnots, input_flip_control_and_target
    )
    assert actual_simplified == expected_simplified
    assert actual_output_cnots == expected_output_cnots
