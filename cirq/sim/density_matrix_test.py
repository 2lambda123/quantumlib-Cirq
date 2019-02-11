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

import itertools

import numpy as np
import pytest

import cirq


def assert_valid_density_matrix(matrix, num_qubits=1):
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(matrix, num_qubits=num_qubits,
                                     dtype=matrix.dtype), matrix)


def test_to_valid_density_matrix_from_density_matrix():
    assert_valid_density_matrix(np.array([[1, 0], [0, 0]]))
    assert_valid_density_matrix(np.array([[0.5, 0], [0, 0.5]]))
    assert_valid_density_matrix(np.array([[0.5, 0.5], [0.5, 0.5]]))
    assert_valid_density_matrix(np.array([[0.5, 0.2], [0.2, 0.5]]))
    assert_valid_density_matrix(np.array([[0.5, 0.5j], [-0.5j, 0.5]]))
    assert_valid_density_matrix(
        np.array([[0.5, 0.2 - 0.2j], [0.2 + 0.2j, 0.5]]))
    assert_valid_density_matrix(np.eye(4) / 4.0, num_qubits=2)
    assert_valid_density_matrix(np.diag([1, 0, 0, 0]), num_qubits=2)
    assert_valid_density_matrix(np.ones([4, 4]) / 4.0, num_qubits=2)
    assert_valid_density_matrix(np.diag([0.2, 0.8, 0, 0]), num_qubits=2)
    assert_valid_density_matrix(np.array(
        [[0.2, 0, 0, 0.2 - 0.3j],
         [0, 0, 0, 0],
         [0, 0, 0, 0],
         [0.2 + 0.3j, 0, 0, 0.8]]),
        num_qubits=2)


def test_to_valid_density_matrix_not_square():
    with pytest.raises(ValueError, match='square'):
        cirq.to_valid_density_matrix(np.array([[1, 0]]), num_qubits=1)
    with pytest.raises(ValueError, match='square'):
        cirq.to_valid_density_matrix(np.array([[1], [0]]), num_qubits=1)


def test_to_valid_density_matrix_size_mismatch_num_qubits():
    with pytest.raises(ValueError, match='size'):
        cirq.to_valid_density_matrix(np.array([[1, 0], [0, 0]]), num_qubits=2)
    with pytest.raises(ValueError, match='size'):
        cirq.to_valid_density_matrix(np.eye(4) / 4.0, num_qubits=1)


def test_to_valid_density_matrix_not_hermitian():
    with pytest.raises(ValueError, match='hermitian'):
        cirq.to_valid_density_matrix(np.array([[1, 0.1], [0, 0]]), num_qubits=1)
    with pytest.raises(ValueError, match='hermitian'):
        cirq.to_valid_density_matrix(np.array([[0.5, 0.5j], [0.5, 0.5j]]),
                                     num_qubits=1)
    with pytest.raises(ValueError, match='hermitian'):
        cirq.to_valid_density_matrix(
            np.array(
                [[0.2, 0, 0, -0.2 - 0.3j],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0],
                 [0.2 + 0.3j, 0, 0, 0.8]]),
            num_qubits=2)


def test_to_valid_density_matrix_not_unit_trace():
    with pytest.raises(ValueError, match='trace 1'):
        cirq.to_valid_density_matrix(np.array([[1, 0], [0, 0.1]]), num_qubits=1)
    with pytest.raises(ValueError, match='trace 1'):
        cirq.to_valid_density_matrix(np.array([[1, 0], [0, -0.1]]),
                                     num_qubits=1)
    with pytest.raises(ValueError, match='trace 1'):
        cirq.to_valid_density_matrix(np.zeros([2, 2]), num_qubits=1)


def test_to_valid_density_matrix_not_positive_semidefinite():
    with pytest.raises(ValueError, match='positive semidefinite'):
        cirq.to_valid_density_matrix(
            np.array([[1.1, 0], [0, -0.1]], dtype=np.complex64), num_qubits=1)
    with pytest.raises(ValueError, match='positive semidefinite'):
        cirq.to_valid_density_matrix(
            np.array([[0.6, 0.5], [0.5, 0.4]], dtype=np.complex64),
            num_qubits=1)


def test_to_valid_density_matrix_wrong_dtype():
    with pytest.raises(ValueError, match='dtype'):
        cirq.to_valid_density_matrix(
            np.array([[1, 0], [0, 0]], dtype=np.complex64),
            num_qubits=1, dtype=np.complex128)


def test_to_valid_density_matrix_from_state():
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(
            density_matrix_rep=np.array([1, 0], dtype=np.complex64),
            num_qubits=1),
        np.array([[1, 0], [0, 0]]))
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(
            density_matrix_rep=np.array([np.sqrt(0.3), np.sqrt(0.7)],
                                        dtype=np.complex64),
            num_qubits=1),
        np.array([[0.3, np.sqrt(0.3 * 0.7)], [np.sqrt(0.3 * 0.7), 0.7]]))
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(
            density_matrix_rep=np.array([np.sqrt(0.5), np.sqrt(0.5) * 1j],
                                        dtype=np.complex64),
            num_qubits=1),
        np.array([[0.5, -0.5j], [0.5j, 0.5]]))
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(
            density_matrix_rep=np.array([0.5] * 4, dtype=np.complex64),
            num_qubits=2),
        0.25 * np.ones((4, 4)))


def test_to_valid_density_matrix_from_state_invalid_state():
    with pytest.raises(ValueError, match="2 qubits"):
        cirq.to_valid_density_matrix(np.array([1, 0]), num_qubits=2)


def test_to_valid_density_matrix_from_computational_basis():
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(density_matrix_rep=0, num_qubits=1),
        np.array([[1, 0], [0, 0]]))
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(density_matrix_rep=1, num_qubits=1),
        np.array([[0, 0], [0, 1]]))
    np.testing.assert_almost_equal(
        cirq.to_valid_density_matrix(density_matrix_rep=2, num_qubits=2),
        np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]))


def test_to_valid_density_matrix_from_state_invalid_computational_basis():
    with pytest.raises(ValueError, match="positive"):
        cirq.to_valid_density_matrix(-1, num_qubits=2)


def test_sample_density_matrix_big_endian():
    results = []
    for x in range(8):
        matrix = cirq.to_valid_density_matrix(x, 3)
        sample = cirq.sample_density_matrix(matrix, [2, 1, 0])
        results.append(sample)
    expecteds = [[list(reversed(x))] for x in
                 list(itertools.product([False, True], repeat=3))]
    for result, expected in zip(results, expecteds):
        np.testing.assert_equal(result, expected)


def test_sample_density_matrix_partial_indices():
    for index in range(3):
        for x in range(8):
            matrix = cirq.to_valid_density_matrix(x, 3)
            np.testing.assert_equal(cirq.sample_density_matrix(matrix, [index]),
                                    [[bool(1 & (x >> (2 - index)))]])

def test_sample_density_matrix_partial_indices_oder():
    for x in range(8):
        matrix = cirq.to_valid_density_matrix(x, 3)
        expected = [[bool(1 & (x >> 0)), bool(1 & (x >> 1))]]
        np.testing.assert_equal(cirq.sample_density_matrix(matrix, [2, 1]),
                                expected)


def test_sample_density_matrix_partial_indices_all_orders():
    for perm in itertools.permutations([0, 1, 2]):
        for x in range(8):
            matrix = cirq.to_valid_density_matrix(x, 3)
            expected = [[bool(1 & (x >> (2 - p))) for p in perm]]
            np.testing.assert_equal(cirq.sample_density_matrix(matrix, perm),
                                    expected)


def test_sample_density_matrix():
    state = np.zeros(8, dtype=np.complex64)
    state[0] = 1 / np.sqrt(2)
    state[2] = 1 / np.sqrt(2)
    matrix = cirq.to_valid_density_matrix(state, num_qubits=3)
    for _ in range(10):
        sample = cirq.sample_density_matrix(matrix, [2, 1, 0])
        assert (np.array_equal(sample, [[False, False, False]])
                or np.array_equal(sample, [[False, True, False]]))
    # Partial sample is correct.
    for _ in range(10):
        np.testing.assert_equal(cirq.sample_density_matrix(matrix, [2]),
                                [[False]])
        np.testing.assert_equal(cirq.sample_density_matrix(matrix, [0]),
                                [[False]])


def test_sample_empty_density_matrix():
    matrix = np.array([])
    assert cirq.sample_density_matrix(matrix, []) == [[]]


def test_sample_density_matrix_no_repetitions():
    matrix = cirq.to_valid_density_matrix(0, 3)
    assert cirq.sample_density_matrix(matrix, [1], repetitions=0) == [[]]


def test_sample_density_matrix_repetitions():
    for perm in itertools.permutations([0, 1, 2]):
        for x in range(8):
            matrix = cirq.to_valid_density_matrix(x, 3)
            expected = [[bool(1 & (x >> (2 - p))) for p in perm]] * 3

            result = cirq.sample_density_matrix(matrix, perm, repetitions=3)
            np.testing.assert_equal(result, expected)


def test_sample_density_matrix_negative_repetitions():
    matrix = cirq.to_valid_density_matrix(0, 3)
    with pytest.raises(ValueError, match='-1'):
        cirq.sample_density_matrix(matrix, [1], repetitions=-1)


def test_sample_density_matrix_not_square():
    with pytest.raises(ValueError, match='not square'):
        cirq.sample_density_matrix(np.array([1, 0, 0]), [1])


def test_sample_density_matrix_not_power_of_two():
    with pytest.raises(ValueError, match='power of two'):
        cirq.sample_density_matrix(np.ones((3, 3)) / 3, [1])
    with pytest.raises(ValueError, match='power of two'):
        cirq.sample_density_matrix(np.ones((2, 3, 2, 3)) / 6, [1])


def test_sample_density_matrix_higher_powers_of_two():
    with pytest.raises(ValueError, match='powers of two'):
        cirq.sample_density_matrix(np.ones((2, 4, 2, 4)) / 8, [1])


def test_sample_density_matrix_out_of_range():
    matrix = cirq.to_valid_density_matrix(0, 3)
    with pytest.raises(IndexError, match='-2'):
        cirq.sample_density_matrix(matrix, [-2])
    with pytest.raises(IndexError, match='3'):
        cirq.sample_density_matrix(matrix, [3])


def test_sample_state_no_indices():
    matrix = cirq.to_valid_density_matrix(0, 3)
    bits = cirq.sample_density_matrix(matrix, [])
    assert [[]] == bits


def test_sample_state_empty_state():
    matrix = np.array([])
    bits = cirq.sample_density_matrix(matrix, [])
    assert [[]] == bits


def test_measure_density_matrix_computational_basis():
    results = []
    for x in range(8):
        matrix = cirq.to_valid_density_matrix(x, 3)
        bits, out_matrix = cirq.measure_density_matrix(matrix, [2, 1, 0])
        results.append(bits)
        np.testing.assert_almost_equal(out_matrix, matrix)
    expected = [list(reversed(x)) for x in
                list(itertools.product([False, True], repeat=3))]
    assert results == expected


def test_measure_density_matrix_computational_basis_reversed():
    results = []
    for x in range(8):
        matrix = cirq.to_valid_density_matrix(x, 3)
        bits, out_matrix = cirq.measure_density_matrix(matrix, [0, 1, 2])
        results.append(bits)
        np.testing.assert_almost_equal(out_matrix, matrix)
    expected = [list(x) for x in
                list(itertools.product([False, True], repeat=3))]
    assert results == expected


def test_measure_density_matrix_computational_basis_reshaped():
    results = []
    for x in range(8):
        matrix = np.reshape(cirq.to_valid_density_matrix(x, 3), (2,) * 6)
        bits, out_matrix = cirq.measure_density_matrix(matrix, [2, 1, 0])
        results.append(bits)
        np.testing.assert_almost_equal(out_matrix, matrix)
    expected = [list(reversed(x)) for x in
                list(itertools.product([False, True], repeat=3))]
    assert results == expected


def test_measure_density_matrix_partial_indices():
    for index in range(3):
        for x in range(8):
            matrix = cirq.to_valid_density_matrix(x, 3)
            bits, out_matrix = cirq.measure_density_matrix(matrix, [index])
            np.testing.assert_almost_equal(out_matrix, matrix)
            assert bits == [bool(1 & (x >> (2 - index)))]


def test_measure_density_matrix_partial_indices_all_orders():
    for perm in itertools.permutations([0, 1, 2]):
        for x in range(8):
            matrix = cirq.to_valid_density_matrix(x, 3)
            bits, out_matrix = cirq.measure_density_matrix(matrix, perm)
            np.testing.assert_almost_equal(matrix, out_matrix)
            assert bits == [bool(1 & (x >> (2 - p))) for p in perm]


def matrix000plus010():
    state = np.zeros(8, dtype=np.complex64)
    state[0] = 1 / np.sqrt(2)
    state[2] = 1j / np.sqrt(2)
    return cirq.to_valid_density_matrix(state, num_qubits=3)


def test_measure_density_matrix_collapse():
    matrix = matrix000plus010()
    for _ in range(10):
        bits, out_matrix = cirq.measure_density_matrix(matrix, [2, 1, 0])
        assert bits in [[False, False, False], [False, True, False]]
        expected = np.zeros(8, dtype=np.complex64)
        if bits[1]:
            expected[2] = 1j
        else:
            expected[0] = 1
        expected_matrix = np.outer(np.conj(expected), expected)
        np.testing.assert_almost_equal(out_matrix, expected_matrix)
        assert out_matrix is not matrix

    # Partial sample is correct.
    for _ in range(10):
        bits, out_matrix = cirq.measure_density_matrix(matrix, [2])
        np.testing.assert_almost_equal(out_matrix, matrix)
        assert bits == [False]

        bits, out_matrix = cirq.measure_density_matrix(matrix, [0])
        np.testing.assert_almost_equal(out_matrix, matrix)
        assert bits == [False]


def test_measure_density_matrix_out_is_state():
    matrix = matrix000plus010()
    bits, out_matrix = cirq.measure_density_matrix(matrix, [2, 1, 0],
                                                   out=matrix)
    expected_state = np.zeros(8, dtype=np.complex64)
    expected_state[2 if bits[1] else 0] = 1.0
    expected_matrix = np.outer(np.conj(expected_state), expected_state)
    np.testing.assert_array_almost_equal(out_matrix, expected_matrix)
    assert out_matrix is matrix


def test_measure_state_out_is_not_state():
    matrix = matrix000plus010()
    out = np.zeros_like(matrix)
    _, out_matrix = cirq.measure_density_matrix(matrix, [2, 1, 0], out=out)
    assert out is not matrix
    assert out is out_matrix


def test_measure_density_matrix_not_square():
    with pytest.raises(ValueError, match='not square'):
        cirq.measure_density_matrix(np.array([1, 0, 0]), [1])


def test_measure_density_matrix_not_power_of_two():
    with pytest.raises(ValueError, match='power of two'):
        cirq.measure_density_matrix(np.ones((3, 3)) / 3, [1])
    with pytest.raises(ValueError, match='power of two'):
        cirq.measure_density_matrix(np.ones((2, 3, 2, 3)) / 6, [1])


def test_measure_density_matrix_higher_powers_of_two():
    with pytest.raises(ValueError, match='powers of two'):
        cirq.measure_density_matrix(np.ones((2, 4, 2, 4)) / 8, [1])


def test_measure_density_matrix_out_of_range():
    matrix = cirq.to_valid_density_matrix(0, 3)
    with pytest.raises(IndexError, match='-2'):
        cirq.measure_density_matrix(matrix, [-2])
    with pytest.raises(IndexError, match='3'):
        cirq.measure_density_matrix(matrix, [3])


def test_measure_state_no_indices():
    matrix = cirq.to_valid_density_matrix(0, 3)
    bits, state = cirq.measure_state_vector(matrix, [])
    assert [] == bits
    np.testing.assert_almost_equal(state, matrix)


def test_measure_state_empty_state():
    matrix = np.array([])
    bits, out_matrix = cirq.measure_state_vector(matrix, [])
    assert [] == bits
    np.testing.assert_almost_equal(matrix, out_matrix)
